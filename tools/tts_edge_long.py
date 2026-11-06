"""Long-form voiceover with Microsoft Edge neural voices and exact word timings.
Same output shape as tts_long.py (scenes -> sentences) plus per-sentence 'words'.
Usage: tts_edge_long.py EP   (needs SSL_CERT_FILE and HTTPS_PROXY)
"""
import asyncio, json, os, re, sys, time, hashlib, subprocess
import numpy as np, soundfile as sf, edge_tts

EP = sys.argv[1]
cfg = json.load(open(f"{EP}/script.json"))
SR = 24000
SENT_GAP, SCENE_GAP, CHAPTER_GAP = 0.18, 0.42, 2.2
os.makedirs(f"{EP}/tts_cache", exist_ok=True)

def sentences(text):
    return [s for s in re.split(r'(?<=[.?!])\s+', text.strip()) if s]

async def synth(text):
    say = text
    for a, b in cfg.get("say", {}).items(): say = say.replace(a, b)
    key = hashlib.md5(f"{cfg['voice']}|{cfg['rate']}|{cfg['pitch']}|{say}".encode()).hexdigest()
    cp = f"{EP}/tts_cache/{key}"
    if os.path.exists(cp + ".npy"):
        return np.load(cp + ".npy"), json.load(open(cp + ".json"))
    for attempt in range(8):
        try:
            c = edge_tts.Communicate(say, cfg["voice"], rate=cfg["rate"], pitch=cfg["pitch"], proxy=os.environ["HTTPS_PROXY"], boundary="WordBoundary")
            audio = b""; words = []
            async for ch in c.stream():
                if ch["type"] == "audio": audio += ch["data"]
                elif ch["type"] == "WordBoundary":
                    words.append({"w": ch["text"], "s": ch["offset"] / 1e7, "e": (ch["offset"] + ch["duration"]) / 1e7})
            if audio and words: break
        except Exception as e:
            print("  retry", attempt, type(e).__name__, flush=True)
        time.sleep(2 + attempt * 2.5)
    else:
        raise RuntimeError("TTS failed: " + text[:60])
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", "pipe:0", "-f", "f32le", "-ac", "1", "-ar", str(SR), "pipe:1"], input=audio, capture_output=True, check=True)
    a = np.frombuffer(p.stdout, np.float32).copy()
    idx = np.where(np.abs(a) > 0.008)[0]
    st = max(idx[0] - 240, 0); a = a[st: idx[-1] + 1400]
    words = [{"w": w["w"], "s": w["s"] - st / SR, "e": w["e"] - st / SR} for w in words]
    np.save(cp + ".npy", a); json.dump(words, open(cp + ".json", "w"))
    return a, words

async def main():
    out = [np.zeros(int(SR * 0.4), np.float32)]; t = 0.4
    scenes, prev = [], None
    for i, sc in enumerate(cfg["scenes"]):
        chs = sc["ch"] != prev
        if chs and i > 0:
            out.append(np.zeros(int(SR * CHAPTER_GAP), np.float32)); t += CHAPTER_GAP
        prev = sc["ch"]
        sents = []; s0 = t
        for s in sentences(sc["text"]):
            a, words = await synth(s)
            d = len(a) / SR
            # map displayed words: keep the spoken tokens' timing, but show the script's own words
            shown = s.split()
            if len(words) == len(shown):
                ws = [{"w": shown[j], "s": t + words[j]["s"], "e": t + words[j]["e"]} for j in range(len(shown))]
            else:
                tot = sum(len(x) + 2 for x in shown); acc = 0; ws = []
                for x in shown:
                    ws.append({"w": x, "s": t + d * acc / tot, "e": t + d * (acc + len(x) + 2) / tot}); acc += len(x) + 2
            sents.append({"text": s, "start": t, "end": t + d, "words": ws})
            out.append(a); t += d
            out.append(np.zeros(int(SR * SENT_GAP), np.float32)); t += SENT_GAP
        out.append(np.zeros(int(SR * (SCENE_GAP - SENT_GAP)), np.float32)); t += SCENE_GAP - SENT_GAP
        scenes.append({"i": i, "ch": sc["ch"], "visual": sc["visual"], "chapter_start": chs, "start": s0, "end": sents[-1]["end"], "sentences": sents})
        print(f"{i:2d} {sc['visual']:14s} {s0:7.2f} -> {sents[-1]['end']:7.2f}", flush=True)
    out.append(np.zeros(int(SR * 1.5), np.float32)); t += 1.5
    full = np.concatenate(out); full = full / np.max(np.abs(full)) * 0.9
    sf.write(f"{EP}/voice.wav", full, SR)
    json.dump({"total": len(full) / SR, "scenes": scenes}, open(f"{EP}/timing.json", "w"), indent=1)
    print("total", round(len(full) / SR, 2))

asyncio.run(main())
