#!/usr/bin/env bash
# Build the Russian TikTok version of an episode (Edge neural TTS voice).
# Usage: tools/make_ru.sh episodes/YYYY-MM-DD_slug     (uses episodes/<ep>/ru/script.json + visuals.py)
# Output: videos/ru/YYYY-MM-DD_slug.mp4
set -euo pipefail
SRC="$(cd "$1" && pwd)"
NAME="$(basename "$SRC")"
EP="$SRC/ru"
[ -f "$EP/script.json" ] || { echo "missing $EP/script.json"; exit 1; }
REPO="$(cd "$(dirname "$0")/.." && pwd)"
export SSL_CERT_FILE="${SSL_CERT_FILE:-/root/.ccr/ca-bundle.crt}"

# 1. Dependencies
pip install --break-system-packages -q edge-tts soundfile numpy pillow >/dev/null 2>&1 || true

# 2. Voiceover -> voice.wav + timing.json
python3 "$REPO/tools/tts_edge.py" "$EP"

# 3. Render + loudness normalisation
python3 "$REPO/tools/render.py" "$EP" "$EP/raw.mp4"
mkdir -p "$REPO/videos/ru"
ffmpeg -v error -y -i "$EP/raw.mp4" -c:v copy -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:a aac -b:a 192k -movflags +faststart "$REPO/videos/ru/$NAME.mp4"
rm -f "$EP/raw.mp4" "$EP/mix.wav" "$EP/voice.wav" "$EP"/preview_*.png
echo "OK $REPO/videos/ru/$NAME.mp4"
