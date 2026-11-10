"""asr_check.py EP -> transcribe each sentence of voice.wav and flag word mismatches."""
import json, re, sys, os
import numpy as np, soundfile as sf
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
from faster_whisper import WhisperModel
EP = sys.argv[1]
tim = json.load(open(f"{EP}/timing.json")); a, sr = sf.read(f"{EP}/voice.wav")
m = WhisperModel(sys.argv[2] if len(sys.argv) > 2 else "small.en", device="cpu", compute_type="int8")
def norm(s):
    s = s.lower().replace("%", " percent").replace("-", " ")
    return re.sub(r"[^a-z0-9 ]", "", s).split()
bad = 0
for sc in tim["scenes"]:
    for se in sc["sentences"]:
        seg = a[int(se["start"] * sr): int(se["end"] * sr) + int(0.1 * sr)].astype(np.float32)
        if sr != 16000:
            import scipy.signal as ss; seg = ss.resample_poly(seg, 16000, sr).astype(np.float32)
        txt = " ".join(x.text for x in m.transcribe(seg, language="en", beam_size=5)[0]).strip()
        A, B = set(norm(se["text"])), set(norm(txt))
        miss = [w for w in norm(se["text"]) if w not in B and not w.isdigit()]
        flag = "!!" if miss else "  "
        if miss: bad += 1
        print(f"{flag} [{sc['visual']}] {se['text']}\n     ASR: {txt}" + (f"\n     missing: {miss}" if miss else ""), flush=True)
print("flagged", bad)
