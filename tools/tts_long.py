"""Voiceover for long-form videos.
Synthesises each sentence separately (Kokoro has a length limit per call), records
per-sentence timing for captions, and inserts a pause before every new chapter.
Usage: tts_long.py EP   (EP has script.json) -> voice.wav + timing.json
"""
import json, os, re, sys
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro

EP = sys.argv[1]
cfg = json.load(open(f"{EP}/script.json"))
kd = os.environ.get("KOKORO_DIR", "/home/claude/tts")
k = Kokoro(f"{kd}/kokoro.onnx", f"{kd}/voices.bin")
SR = 24000
SENT_GAP, SCENE_GAP, CHAPTER_GAP = 0.16, 0.38, 2.2

def sentences(text):
    parts = re.split(r'(?<=[.?!])\s+', text.strip())
    return [s for s in parts if s]

import hashlib
os.makedirs(f"{EP}/tts_cache", exist_ok=True)
def synth(text):
    for a, b in cfg.get("say", {}).items():
        text = text.replace(a, b)
    key = hashlib.md5(f"{cfg['voice']}|{cfg['speed']}|{text}".encode()).hexdigest()
    cp = f"{EP}/tts_cache/{key}.npy"
    if os.path.exists(cp):
        return np.load(cp)
    a = _synth(text); np.save(cp, a); return a

def _synth(text):
    audio, sr = k.create(text, voice=cfg["voice"], speed=cfg["speed"], lang="en-us")
    assert sr == SR
    audio = audio.astype(np.float32)
    idx = np.where(np.abs(audio) > 0.01)[0]
    return audio[max(idx[0] - 600, 0): idx[-1] + 1500]

out = [np.zeros(int(SR * 0.4), np.float32)]
t = 0.4
scenes, prev_ch = [], None
for i, sc in enumerate(cfg["scenes"]):
    chapter_start = sc["ch"] != prev_ch
    if chapter_start and i > 0:
        out.append(np.zeros(int(SR * CHAPTER_GAP), np.float32)); t += CHAPTER_GAP
    prev_ch = sc["ch"]
    sents = []
    s_start = t
    for j, s in enumerate(sentences(sc["text"])):
        a = synth(s)
        d = len(a) / SR
        sents.append({"text": s, "start": t, "end": t + d})
        out.append(a); t += d
        out.append(np.zeros(int(SR * SENT_GAP), np.float32)); t += SENT_GAP
    out.append(np.zeros(int(SR * (SCENE_GAP - SENT_GAP)), np.float32)); t += SCENE_GAP - SENT_GAP
    scenes.append({"i": i, "ch": sc["ch"], "visual": sc["visual"], "chapter_start": chapter_start,
                   "start": s_start, "end": sents[-1]["end"], "sentences": sents})
    print(f"{i:2d} {sc['visual']:15s} {s_start:7.2f} -> {sents[-1]['end']:7.2f}", flush=True)
out.append(np.zeros(int(SR * 1.5), np.float32)); t += 1.5
full = np.concatenate(out)
full = full / np.max(np.abs(full)) * 0.9
sf.write(f"{EP}/voice.wav", full, SR)
json.dump({"total": len(full) / SR, "scenes": scenes}, open(f"{EP}/timing.json", "w"), indent=1)
print("total", len(full) / SR)
