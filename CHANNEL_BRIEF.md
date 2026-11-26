# EV DRIVE — channel brief for the daily Short (and long videos)

This file is the standing instruction for every daily run. Follow it exactly.

## Channel
- Name: **EV DRIVE** (YouTube Shorts, English, US audience)
- Theme: electric cars, automotive technology, car software, hidden features, futuristic vehicles.
- Goal set by the owner (updated 2026-11-08): act as an experienced YouTube content strategist for automotive tech, EVs, Tesla, Chinese EV makers and futuristic engineering. Every video must still teach one real, fact-checked idea, but **no generic textbook topics** ("How X works" on its own is not allowed). Wrap the lesson in a story people want to click, watch to the end, and argue about in the comments. Broad audience first: a non-car person must understand the title in 2 seconds.

## Content strategy (pick every topic through this)
Topics must come from at least one of these angles:
1. **Controversial automotive facts** — true facts that start arguments (EVs cost 49% more to insure; brand-new cars sold as "used" in China).
2. **Hidden problems with EVs** — real downsides, told honestly, with numbers (door handles that won't open after a crash, tire wear, repair costs).
3. **Technologies that seem impossible** — 5-minute charging, 500 km/h EVs, no-lithium batteries, a car that spins like a tank.
4. **Surprising comparisons between manufacturers** — Tesla vs BYD, Xiaomi vs Porsche, Tesla vs Waymo, China vs Germany.
5. **Experiments and hypothetical scenarios** — "What if every car went electric tomorrow?", "EV vs gas car stuck in a blizzard".
6. **Unusual engineering** — steer-by-wire, 1,200-volt platforms, battery swapping, fake gear shifts.
7. **Fresh news from Tesla, BYD, Xiaomi, NIO, Li Auto, Zeekr, Mercedes and others** — always search the last 2–4 weeks of news first; a topic tied to this week's news beats an evergreen one.

How to choose (every run):
- First run a quick news search (WebSearch, e.g. "EV news this week", "Tesla news", "BYD news", "Xiaomi EV news"). If something big and checkable broke in the last 14 days, make the Short about it.
- Otherwise take the highest-ranked unused idea from `ideas_bank.md` (mark it used there, with date and slot). Shorts may use one part of a big idea (its hook, its mid-video reveal, or its ending question).
- Score the chosen topic on: broad appeal 30% · emotion (fear, money, awe, rivalry) 25% · timeliness 20% · debate potential 15% · visual payoff 10%. Prefer the highest score; never repeat a topic in `topics_log.md` unless there is a genuinely new angle or news peg.
- The two Shorts of the same day must use different angles from the list above.

Every Short is built as: **hook** (a surprising claim or uncomfortable question in the first sentence, never "Today we'll learn…") → **story** (a rivalry, a mystery, a problem, a record) → **mid-point reveal** (the unexpected fact that pays off the title) → **ending** with a question that makes people comment (pick a side, guess a number, would you…?), then the "Follow EV Drive" line.

Honesty rules stay absolute: fact-check every claim with WebSearch/WebFetch, no invented numbers, no false claims about any brand, present both sides on controversial questions, and the video must clearly deliver what the title promises.

## Script rules
- 30–45 seconds spoken (roughly 85–115 words). Hook in the first sentence (a question or a surprising claim).
- 5–7 scenes, one idea per scene, plain words, numbers spelled the way they should be spoken.
- **Fact-check every claim with WebSearch/WebFetch before using it.** Prefer regulators, manufacturers, universities, peer-reviewed or engineering sources. If a claim can't be verified, drop it. No invented statistics. Hedge ranges honestly ("about", "up to").
- No brand logos, no copyrighted footage, no real people's likenesses. Brands may be named factually.
- Avoid repeating a topic listed in `topics_log.md`.

## Visual style: REAL FOOTAGE (owner's decision, 2026-11-14 — use this for every Short from now on)
The owner chose real video footage with numbers on top (reference: `videos/footage_fast_charging.mp4`, episode `footage/2026-11-14_fast-charging/`). The older graphics-only engine (`tools/render.py`), the 3D-car look and the cartoon story engine (`tools/render_story.py`) are no longer the default; use them only if the owner asks.
- 1080×1920, 30 fps. Real stock clips fill the whole frame; overlays carry the facts.
- **Use plenty of footage (owner: "a bit more footage"):** 2–3 different clips per scene, a new shot every 2–3 seconds, at least 10 shots per Short, and never the same clip twice in a row. Don't reuse the exact clip set of the previous two Shorts.
- Choose clips from `footage/LIBRARY.md` by what they show, matching what is being said (charging talk → charging clips, cost → money or mechanic, winter → snow roads, software → screens). Never present a generic clip as a specific model, brand or news event, and avoid clips the library marks as showing a logo.
- Overlays (`overlays.py`): one idea per scene — a big number, a 2-bar comparison, a battery gauge, a label pill. Keep them between y=380 and y=1000; captions sit at y≈1360; nothing important below y=1550. Don't repeat the spoken sentence as text. Show the source on screen once when a study is quoted.
- Captions (1–3 words, spoken word in yellow), the EV DRIVE badge, the progress bar, music and whooshes are added by the engine.
- If a story needs something the library doesn't have (a specific car, a record run), tell it with overlays over neutral clips (highway, city, factory) and say so honestly in words; do not fake footage.

## Engine for real-footage Shorts (in `tools/`)
1. Episode folder `footage/YYYY-MM-DD_slug/` with `script.json`: `{title, voice: "en-US-AndrewMultilingualNeural", rate: "+12%", pitch: "+0Hz", say: {}, chapters: {"s": "s"}, scenes: [{ch: "s", visual: "<name>", text: "...", clips: ["9790187_a.mp4", {"clip": "13979384_a.mp4", "ss": 3, "speed": 0.7}]}]}`. 5–7 scenes, 70–100 words in total (about 30–40 s).
2. Voice: `export SSL_CERT_FILE=/root/.ccr/ca-bundle.crt && python3 tools/tts_edge_long.py footage/<ep>` → `voice.wav` + `timing.json` (needs `pip install edge-tts --break-system-packages`; retries are built in). If Edge TTS keeps failing after 3 tries, stop and report to the owner rather than switching voice.
3. Check the voice: `HF_HUB_DISABLE_XET=1 python3 tools/asr_check.py footage/<ep>` (needs `faster-whisper`). Reword any sentence where a word other than a number is flagged, then regenerate. Avoid abbreviations the voice mangles: write "electric cars", not "EVs".
4. `overlays.py` in the episode folder: one `ov_<visual>(d, lt, t, s)` per scene, using the helpers `pill`, `card`, `text`, `rect`, `battery`, `pop`, `smooth`, `clamp`, `mix`, `sent(s, k)` (start time of sentence k inside the scene) and the colours `LIME, YELLOW, ORANGE, RED, GREEN, WHITE, INK`. Copy the pattern from `footage/2026-11-14_fast-charging/overlays.py`. Time each reveal to the sentence that says it.
5. Preview then render: `python3 tools/render_footage.py footage/<ep> preview t1,t2,...` (one time per clip, so every shot is checked) → Read the PNGs and fix overlaps, unreadable text or a clip that doesn't match the words. Then `python3 tools/render_footage.py footage/<ep> videos/<file>.mp4`.
6. After rendering, extract a frame strip (`ffmpeg -i videos/<file>.mp4 -vf "fps=1/2.5,scale=180:-1,tile=14x1" -frames:v 1 strip.jpg`) and look at it once more before scheduling.
- Thumbnails/covers for Shorts: use a strong frame of the video itself (the first scene with its hook overlay) saved as `thumbs/<episode>.jpg`; the `tools/thumbnail.py` 3D-car covers are optional.
- The CC BY credit line for the 3D car is needed only when the 3D car actually appears.

## 3D car (only when the owner asks for the 3D look; not used in real-footage Shorts)
- The only car model to use is the photoreal **Car Concept** in `test3d/models/CarConcept.glb` (full interior, metallic clearcoat paint, real wheels/brakes, opening doors), rendered by `test3d/realcar.js` with a studio softbox environment and contact shadows. The old procedural/blobby car is retired: never draw a car from primitives again.
- Setup in a fresh run: `cd test3d && npm install three@0.169.0` (node_modules is not committed).
- Stills / transparent PNGs: `python3 test3d/render_real.py OUTDIR poses.json [W H]` with poses like `{"ang":0.6,"dist":8,"h":1.4,"paint":"red"}`. Options: `paint` (red, white, black, silver, blue, lime, orange, gray, teal or a hex), `xray: true` (ghost body + glowing battery pack, `packColor: "hot"`), `brake: true`, `bg` (colour or omit for transparent), `env` (studio, venice_sunset, quarry_01, moonless_golf), `fov`, `ty`. Ready-made transparent renders are in `assets/cars/` (see `test3d/poses_real.json`).
- Animated shots: render a sequence of poses (one per frame) with the same script and assemble with ffmpeg.
- **Credit is required (CC BY 4.0):** every video or thumbnail that shows this car must have this line in the description, just before the hashtags: `3D car model: "Car Concept" by Eric Chadwick / Darmstadt Graphics Group (CC BY 4.0)`.
- Never show logos: the renderer already hides the licence plate and blanks the tyre-sidewall text.
- **Default look = modern Chinese premium EV design language** (owner's request, 2026-11-08): full-width front light bar, red full-width rear light bar, roof lidar pod, two-tone black roof/lower body. It is on unless a pose sets `"style":"plain"`; `"roof"` sets the second tone. Never imitate a specific real model (no Li Auto/Zeekr/Avatr/BYD replicas); when a video is about a real brand, name it in words and on-screen text, but show our own generic car.

## Titles (owner's style — curiosity first, always honest)
The owner wants titles that make people click, in the style of these pairs (educational → clickable):
- How EV Batteries Work → "The Battery Inside Your Tesla Is More Complicated Than You Think"
- How Self-Driving Cars Work → "Tesla's Self-Driving Technology Has a Serious Problem"
- How EV Charging Works → "Why Charging Your EV Can Be More Expensive Than You Think"
- How Electric Motors Work → "Electric Cars Have Something Gas Cars Don't"
- EV Battery Degradation → "Your Electric Car Battery Is Slowly Dying. Here's Why"
Rules:
- Open a curiosity gap: hint at a surprise, a problem, a secret or a hidden cost, but don't give the answer in the title.
- Speak to the viewer: "Your EV…", "Your Tesla…", "You've been…". Use concrete nouns (battery, brake, charger, Tesla, Porsche) and power words (secretly, hidden, problem, never, really, actually, dying, more than you think).
- Patterns that work: "Your ___ Is Secretly ___" · "Why ___ Is More ___ Than You Think" · "___ Has a Serious Problem" · "___ Have Something ___ Don't" · "___. Here's Why" · "Nobody Tells You This About ___" · "The ___ Nobody Talks About".
- Plain words, no emojis, Title Case, ≤ 60 characters before " #shorts" (Shorts end with " #shorts"; long videos don't).
- **Never lie or exaggerate:** the video must clearly deliver what the title promises. No invented problems, no false claims about a brand, no "shocking" claims the facts don't support. Clickable, never misleading.
- Write 3 candidate titles, pick the strongest, and put the plain educational version in the first line of the description.

## Thumbnails (every video, Shorts included)
- Make one with `tools/thumbnail.py spec.json out.jpg` (see the docstring; examples in `thumbs/specs.json`). Long videos: `"size": "long"` (1280×720). Shorts: `"size": "short"` (1080×1920 cover).
- 2–4 huge words, max 3 lines, **different from the title** (the thumbnail adds the hook, the title explains it). One word in the accent color. Use a number, a question mark or a "!" when it fits ("DIRTIER THAN GAS?", "99.9% ISN'T ENOUGH", "4,416 BATTERIES?").
- One big subject: a 3D car from `assets/cars/` (side views and x-ray views look best) filling about half the frame, and **exactly one** attention device: red arrow, red circle, yellow warning sign, big "?" or a number badge, pointing at what the video explains.
- Bold background theme by mood: red = problem/danger, orange = cost/controversy, blue = cold/charging/tech, lime = how-it-works, purple = history.
- Look at the result (Read the jpg) before using it: text readable at phone size, nothing cut off, subject not hidden.
- Save it as `thumbs/<episode>.jpg`, push, and pass its raw URL as `videoThumbnailUrl` when scheduling (YouTube only shows custom thumbnails on verified channels; it's harmless otherwise). If Metricool rejects it with VIDEO_THUMBNAIL_NOT_APPLICABLE, schedule again without it.
- Shorts: also make the first second of the video itself a strong cover (big hook text on screen), because many viewers see that frame.

## Publishing
- Commit the episode folder + the mp4 in `videos/` and push to `main`.
- Public video URL: `https://raw.githubusercontent.com/ParuyrBaghyan/ev-drive-videos/main/videos/<file>.mp4` (check it returns 200 before scheduling).
- Schedule with Metricool `createScheduledPost`: blogId `7793522` (Metricool account baghyanparuyr@gmail.com; on 2026-11-26 the Metricool connector switched to this account and brand 7616311 / studyfy.support@gmail.com now returns 403 "Access denied to blog"; both brands' free plans were full for November 2026). Use `getBrandSettings` first: if the connected account shows a different brand id that has YouTube (`youtubeData` UCjF5CtSbLc1g9N8ejnaFEuw), use that one instead and update this line, provider `youtube`, `autoPublish: true`, publication time = the run's slot on the run's date (send `publicationDate` with timezone `America/New_York`).
- **Free-plan limit:** a free Metricool account publishes only 20 posts per calendar month (resets on the 1st). Before scheduling, count this calendar month's PUBLISHED + PENDING posts for the brand (getScheduledPosts from the 1st to the end of the month, all networks, including TikTok). If 20 or more, do NOT schedule (it would fail with "You have reached your Metricool account limit"): still make the video and commit it, then tell the owner with SendUserMessage that the month's limit is reached and the video is ready to publish when the limit resets or the plan is upgraded.
- **Two Shorts per day, two slots:** **12:00** (noon run) and **18:00** (evening run), America/New_York. Each scheduled run makes exactly one Short for its own slot.
  youtubeData: `type: "short"`, `privacy: "public"`, `category: "SCIENCE_TECHNOLOGY"`, `madeForKids: false`, `isAiGeneratedContent: false`, 4–8 tags. Title: follow the **Titles** section (curiosity style, ≤ 60 chars + " #shorts", no emojis). Description: first line = the plain educational title, then 2–3 sentences summarising what the viewer learns + hashtags `#EV #ElectricCars #CarTech #EVDrive #shorts`. Add `videoThumbnailUrl` (see **Thumbnails**).
- A slot that already has an entry in `topics_log.md` counts as filled even if Metricool doesn't show it (posts up to 2026-11-02 12:00 ET were scheduled in the old Metricool account) — never make a second video for it.
- Before starting, call `getScheduledPosts` for that day (use `extendedRange: true` so already-published posts show up too) and skip only if a YouTube post already exists **in your own slot** (publication time within ±1 hour of the slot). A post in the other slot is expected — never double-post a slot.
- Before picking a topic, also check today's other-slot post (and `topics_log.md`) so the two Shorts of the day have different topics and angles (see Content strategy).
- Append the episode to `topics_log.md` (date, slot, angle, topic, title, sources) and mark the idea used in `ideas_bank.md` if it came from there and push again.
