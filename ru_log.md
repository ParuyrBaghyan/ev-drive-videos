# EV DRIVE — Russian TikTok log

One Russian TikTok per day at 20:00 Asia/Yerevan, each a Russian version of an English Short.
Voice: Edge `de-DE-FlorianMultilingualNeural`, rate +20%, pitch +8Hz (`tools/make_ru.sh`).

**Pronunciation rule (owner feedback 2026-10-26):** this multilingual voice garbles numbers at the very start of an utterance and decimals like «целых … десятых». Never open a scene with a number; put a few Russian words first (e.g. «В одном галлоне бензина тридцать три и семь десятых…»), say decimals as «X и Y десятых», and avoid accent marks (they break the word). Check the finished audio by transcribing it (faster-whisper `small`, `HF_HUB_DISABLE_XET=1`) before scheduling.

| Source episode | Russian title | Scheduled (Asia/Yerevan) | Video |
|---|---|---|---|
| 2026-10-26_what-is-a-kwh | Что такое киловатт-час на самом деле? ⚡ | 2026-10-26 20:00 (published with garbled opening number); fixed version re-posted 2026-10-26 20:50 | videos/ru/2026-10-26_what-is-a-kwh.mp4 |
| 2026-10-27_12v-battery | У электромобиля есть ВТОРАЯ батарея 🔋 | 2026-10-27 20:00 (video replaced with fixed opening) | videos/ru/2026-10-27_12v-battery.mp4 |
| 2026-10-28_one-gear | 10 передач против ОДНОЙ ⚙️⚡ | 2026-10-28 20:00 | videos/ru/2026-10-28_one-gear.mp4 |
| 2026-10-30_inverter | Как электромобиль «переводит» ток ⚡🔁 | 2026-10-30 20:00 | videos/ru/2026-10-30_inverter.mp4 |
| 2026-10-31_ev-fire-myth | Электромобили горят чаще? Данные 🔥🔋 | 2026-10-31 20:00 | videos/ru/2026-10-31_ev-fire-myth.mp4 |
| 2026-11-01_self-driving-levels | Ваша машина — беспилотник? Шкала от 0 до 5 🚗🤖 | 2026-11-01 20:00 | videos/ru/2026-11-01_self-driving-levels.mp4 |

Note (2026-10-30 run): no RU TikTok exists for the 2026-10-29 20:00 slot (it was missed; past slots are not back-filled). «восемь сотых процента» was heard as «восьмисотых» by the voice in context; «ноль, ноль восемь процента» is said cleanly — prefer that pattern for small percentages.
