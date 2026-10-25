"""Drop-in equivalent of tools/tts.py using Microsoft Edge neural TTS (edge-tts).

Usage: python3 tools/tts_edge.py EPISODE_DIR   (e.g. episodes/<ep>/ru)
Reads voice / rate / pitch from script.json (defaults: de-DE-FlorianMultilingualNeural, +20%, +8Hz).
Writes voice.wav (24 kHz mono) + timing.json with the same padding, gaps and normalisation as tts.py.
Needs SSL_CERT_FILE=/root/.ccr/ca-bundle.crt in this sandbox; the proxy is passed explicitly.
"""
import asyncio, json, os, subprocess, sys, tempfile, time
import numpy as np, soundfile as sf
import edge_tts

base = sys.argv[1]
cfg = json.load(open(f"{base}/script.json"))
VOICE = cfg.get("voice", "de-DE-FlorianMultilingualNeural")
RATE = cfg.get("rate", "+20%")
PITCH = cfg.get("pitch", "+8Hz")
PROXY = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
SR = 24000
if os.path.exists("/root/.ccr/ca-bundle.crt"):
    os.environ.setdefault("SSL_CERT_FILE", "/root/.ccr/ca-bundle.crt")


async def _synth(text, path):
    c = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH, proxy=PROXY)
    await c.save(path)


def synth(text):
    """Synthesize one scene; retry up to 8 times with growing pause (NoAudioReceived etc.)."""
    tmp = tempfile.mkdtemp()
    mp3, wav = f"{tmp}/s.mp3", f"{tmp}/s.wav"
    last = None
    for attempt in range(8):
        try:
            asyncio.run(_synth(text, mp3))
            if os.path.getsize(mp3) < 1000:
                raise RuntimeError("audio too small")
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", mp3, "-ac", "1", "-ar", str(SR), wav], check=True)
            a, _ = sf.read(wav, dtype="float32")
            return a
        except Exception as e:  # noqa
            last = e
            pause = min(20, 2 + attempt * 3)
            print(f"  tts retry {attempt + 1}/8 after {type(e).__name__}: {e}; sleeping {pause}s", flush=True)
            time.sleep(pause)
    raise RuntimeError(f"TTS failed: {last}")


out, timing, t = [], [], 0.25
out.append(np.zeros(int(SR * 0.25), dtype=np.float32))
for s in cfg["scenes"]:
    audio = synth(s["text"])
    idx = np.where(np.abs(audio) > 0.01)[0]
    audio = audio[max(idx[0] - 600, 0): idx[-1] + 1200]
    dur = len(audio) / SR
    timing.append({"id": s["id"], "start": t, "end": t + dur})
    out.append(audio)
    gap = 0.22
    out.append(np.zeros(int(SR * gap), dtype=np.float32))
    t += dur + gap
out.append(np.zeros(int(SR * 0.6), dtype=np.float32))
full = np.concatenate(out)
full = full / np.max(np.abs(full)) * 0.9
sf.write(f"{base}/voice.wav", full, SR)
json.dump({"total": len(full) / SR, "scenes": timing}, open(f"{base}/timing.json", "w"), indent=1)
print(json.dumps(timing, indent=1), len(full) / SR)
