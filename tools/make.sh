#!/usr/bin/env bash
# Build one Short from an episode folder that contains script.json (and optionally visuals.py).
# Usage: tools/make.sh episodes/YYYY-MM-DD_slug
# Output: videos/YYYY-MM-DD_slug.mp4
set -euo pipefail
EP="$(cd "$1" && pwd)"
NAME="$(basename "$EP")"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
export KOKORO_DIR="${KOKORO_DIR:-$HOME/kokoro}"

# 1. Dependencies (fast if already installed)
pip install --break-system-packages -q kokoro-onnx soundfile numpy pillow >/dev/null 2>&1 || true
mkdir -p "$KOKORO_DIR"
[ -s "$KOKORO_DIR/kokoro.onnx" ] || curl -sSL -o "$KOKORO_DIR/kokoro.onnx" https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -s "$KOKORO_DIR/voices.bin" ]  || curl -sSL -o "$KOKORO_DIR/voices.bin"  https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin

# 2. Voiceover -> voice.wav + timing.json
python3 "$REPO/tools/tts.py" "$EP"

# 3. Render video (raw mix) then normalize loudness for YouTube (-14 LUFS)
python3 "$REPO/tools/render.py" "$EP" "$EP/raw.mp4"
mkdir -p "$REPO/videos"
ffmpeg -v error -y -i "$EP/raw.mp4" -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k -movflags +faststart "$REPO/videos/$NAME.mp4"
rm -f "$EP/raw.mp4" "$EP/mix.wav" "$EP/voice.wav" "$EP"/preview_*.png
echo "OK $REPO/videos/$NAME.mp4"
