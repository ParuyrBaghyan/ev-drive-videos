# EV DRIVE — channel brief for the daily Short

This file is the standing instruction for every daily run. Follow it exactly.

## Channel
- Name: **EV DRIVE** (YouTube Shorts, English, US audience)
- Theme: electric cars, automotive technology, car software, hidden features, futuristic vehicles.
- Goal set by the owner: content must be **educational and cognitive**. Each Short teaches ONE real idea and explains *how* or *why* it works, so the viewer leaves smarter, not just entertained.

## Formats (rotate; never use the same format as the previous episode — with two Shorts a day, the noon and evening Shorts of one day must also differ)
1. **How it works** — the mechanism behind a technology (regen braking, heat pumps, LiDAR, inverters).
2. **Myth vs fact** — a common belief, then the evidence.
3. **What would happen if…?** — a thought experiment grounded in real physics/engineering.
4. **The numbers** — one striking figure, then why it is that way (build it up with on-screen counters/comparisons).
5. **History** — a surprising origin story (e.g. early electric cars, the first cruise control).
6. **Hidden feature** — a real feature most owners don't know, and the engineering reason it exists.
Every Short ends with a short thought-provoking question or takeaway before the "Follow EV Drive" line.

## Script rules
- 30–45 seconds spoken (roughly 85–115 words). Hook in the first sentence (a question or a surprising claim).
- 5–7 scenes, one idea per scene, plain words, numbers spelled the way they should be spoken.
- **Fact-check every claim with WebSearch/WebFetch before using it.** Prefer regulators, manufacturers, universities, peer-reviewed or engineering sources. If a claim can't be verified, drop it. No invented statistics. Hedge ranges honestly ("about", "up to").
- No brand logos, no copyrighted footage, no real people's likenesses. Brands may be named factually.
- Avoid repeating a topic listed in `topics_log.md`.

## Visual rules (graphics only — no real footage)
- 1080×1920, 30 fps. Palette: background #0A0D12, accent electric lime #C6FF3D, secondary orange #FF7A3D, text #F4F6F8, muted #788496. Font: Inter / Inter Display (installed).
- Keep important content between y=250 and y=1550 (Shorts UI covers the edges).
- Quality bar (owner asked for better graphics than the first video): labeled diagrams, cutaways, layered shapes with depth (shadows, gradients used sparingly, glow on the accent), smooth eased motion, things that *build up* on screen (counters, bar comparisons, arrows tracing energy flow). Every scene must move; no static slides.
- Captions are handled by the engine (word-highlighted). Don't duplicate the spoken sentence as on-screen text; on-screen text is labels, numbers and key terms.

## Engine (in `tools/`)
- `tools/tts.py EP` → voiceover (Kokoro voice `am_michael`, speed ~1.12) + `timing.json`.
- `tools/render.py EP OUT [t1,t2,...]` → renders the video; with a third argument it only writes preview PNGs at those times (use this to check layout before the full render).
- `tools/make.sh EP` → does everything and writes `videos/<episode>.mp4`.
- An episode folder `episodes/YYYY-MM-DD_slug/` holds `script.json` (see `episodes/2026-10-24_avas/script.json` for the format: title, voice, speed, scenes[{id,text,visual}]) and `visuals.py`.
- `visuals.py` runs inside render.py's globals. Define `vis_<name>(d, lt, t)` functions that draw on a 2× supersampled 900×900 logical canvas (use helpers `p()`, `arc()`, `rgba()`, `text_c()`, `FL()`, `speaker()`, `car_side()`, `person()`, `tire()`, `gauge()`, `waves()`, easing `ease_out/ease_inout/back_out`, colours `ACC/ACC2/WHITE/MUTED/BG`), then register them: `VIS.update({"name": vis_name})`. `lt` = seconds since the scene started, `t` = global time; `scenes[i]` gives start/vis_end. Look at the AVAS visuals in render.py as the reference.
- Always render preview frames for every scene and LOOK at them (Read the PNGs) before the full render. Fix overlaps, clipping and unreadable text.

## Publishing
- Commit the episode folder + the mp4 in `videos/` and push to `main`.
- Public video URL: `https://raw.githubusercontent.com/ParuyrBaghyan/ev-drive-videos/main/videos/<file>.mp4` (check it returns 200 before scheduling).
- Schedule with Metricool `createScheduledPost`: blogId `7616311`, provider `youtube`, `autoPublish: true`, publication time = the run's slot on the run's date (send `publicationDate` with timezone `America/New_York`).
- **Two Shorts per day, two slots:** **12:00** (noon run) and **18:00** (evening run), America/New_York. Each scheduled run makes exactly one Short for its own slot.
  youtubeData: `type: "short"`, `privacy: "public"`, `category: "SCIENCE_TECHNOLOGY"`, `madeForKids: false`, `isAiGeneratedContent: false`, 4–8 tags. Title ≤ 70 chars, ends with `#shorts`. Description: 2–3 sentences summarising what the viewer learns + hashtags `#EV #ElectricCars #CarTech #EVDrive #shorts`.
- Before starting, call `getScheduledPosts` for that day (use `extendedRange: true` so already-published posts show up too) and skip only if a YouTube post already exists **in your own slot** (publication time within ±1 hour of the slot). A post in the other slot is expected — never double-post a slot.
- Before picking a topic, also check today's other-slot post (and `topics_log.md`) so the two Shorts of the day have different topics and formats.
- Append the episode to `topics_log.md` (date, format, topic, title, sources) and push again.
