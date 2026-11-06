"""Edge neural TTS per scene, with exact word timings. -> voice.wav + timing.json"""
import asyncio, json, os, sys, io, subprocess, time
import numpy as np, soundfile as sf, edge_tts
EP = sys.argv[1]; cfg = json.load(open(f"{EP}/script.json"))
SR = 24000; GAP = 0.32
async def synth(text):
    for attempt in range(8):
        try:
            c = edge_tts.Communicate(text, cfg["voice"], rate=cfg["rate"], pitch=cfg["pitch"], proxy=os.environ["HTTPS_PROXY"], boundary="WordBoundary")
            audio = b""; words = []
            async for ch in c.stream():
                if ch["type"] == "audio": audio += ch["data"]
                elif ch["type"] == "WordBoundary":
                    words.append({"w": ch["text"], "s": ch["offset"] / 1e7, "e": (ch["offset"] + ch["duration"]) / 1e7})
            if audio: return audio, words
        except Exception as e:
            print("retry", attempt, e, flush=True)
        time.sleep(2 + attempt * 2.5)
    raise RuntimeError("tts failed")
async def main():
    out = [np.zeros(int(SR * 0.3), np.float32)]; t = 0.3; scenes = []
    for sc in cfg["scenes"]:
        mp3, words = await synth(sc["text"])
        p = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-f", "f32le", "-ac", "1", "-ar", str(SR), "pipe:1"], input=mp3, capture_output=True, check=True)
        a = np.frombuffer(p.stdout, np.float32).copy()
        lead = 0.0
        idx = np.where(np.abs(a) > 0.008)[0]
        if len(idx):
            st = max(idx[0] - 240, 0); lead = st / SR
            a = a[st: idx[-1] + 1200]
        ws = [{"w": w["w"], "s": t + w["s"] - lead, "e": t + w["e"] - lead} for w in words]
        scenes.append({"id": sc["id"], "start": t, "end": t + len(a) / SR, "words": ws, "text": sc["text"]})
        out.append(a); t += len(a) / SR
        out.append(np.zeros(int(SR * GAP), np.float32)); t += GAP
        print(f"{sc['id']:6s} {scenes[-1]['start']:6.2f}-{scenes[-1]['end']:6.2f} words={len(ws)}", flush=True)
    out.append(np.zeros(int(SR * 1.2), np.float32)); t += 1.2
    full = np.concatenate(out); full = full / np.max(np.abs(full)) * 0.9
    sf.write(f"{EP}/voice.wav", full, SR)
    json.dump({"total": len(full) / SR, "scenes": scenes}, open(f"{EP}/timing.json", "w"), indent=1)
    print("total", round(len(full) / SR, 2))
asyncio.run(main())
