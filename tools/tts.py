import json, sys, os
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

base = sys.argv[1]
cfg = json.load(open(f"{base}/script.json"))
k = Kokoro(os.environ.get("KOKORO_DIR", "/home/claude/tts") + "/kokoro.onnx", os.environ.get("KOKORO_DIR", "/home/claude/tts") + "/voices.bin")
out, timing, t = [], [], 0.25
sr = 24000
out.append(np.zeros(int(sr * 0.25), dtype=np.float32))
for s in cfg["scenes"]:
    audio, sr = k.create(s["text"], voice=cfg["voice"], speed=cfg["speed"], lang="en-us")
    audio = audio.astype(np.float32)
    # trim leading/trailing near-silence
    idx = np.where(np.abs(audio) > 0.01)[0]
    audio = audio[max(idx[0] - 600, 0): idx[-1] + 1200]
    dur = len(audio) / sr
    timing.append({"id": s["id"], "start": t, "end": t + dur})
    out.append(audio)
    gap = 0.22
    out.append(np.zeros(int(sr * gap), dtype=np.float32))
    t += dur + gap
out.append(np.zeros(int(sr * 0.6), dtype=np.float32))
full = np.concatenate(out)
full = full / np.max(np.abs(full)) * 0.9
sf.write(f"{base}/voice.wav", full, sr)
json.dump({"total": len(full) / sr, "scenes": timing}, open(f"{base}/timing.json", "w"), indent=1)
print(json.dumps(timing, indent=1), len(full) / sr)
