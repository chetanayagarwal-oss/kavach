# 06 · Build plan (pre-event + 5 hours)

Code is already written. Aaj ka kaam = **run it, test it, tune it, measure it, present it.**
Don't rewrite; improve.

## ⏰ Before you reach LNMIIT (do this at home tonight / early morning)

- [ ] Install Ollama: https://ollama.com
- [ ] `ollama pull gemma4:e4b` (≈9.6 GB) **and** `ollama pull gemma4:e2b` (backup, smaller). **Venue WiFi pe mat karna.**
- [ ] `pip install -r requirements.txt`
- [ ] `python data/make_samples.py`
- [ ] Smoke test: `python -m kavach.cli --text "Share the OTP you just received, urgent" --brief`
- [ ] Note your laptop specs (CPU, RAM, GPU) for the README
- [ ] Create an empty public GitHub repo named `kavach`
- [ ] Charge laptop; carry charger + extension board
- [ ] Register every teammate individually on the MLH page

If `ollama pull` fails at home → try `gemma4:e2b` only, it is smaller.

## Roles (2–4 people)

| Role | Owns | If you are 2 people |
|---|---|---|
| **A · Model & pipeline** | Ollama, prompts, schemas, fusion, eval runs | A + B merge |
| **B · Rules & data** | `rules.py`, extra real samples, labels | A + B merge |
| **C · UI & demo** | `app.py`, demo flow, screen recording | C + D merge |
| **D · Story & submission** | README, slides, pitch, MLH submission, DEV post | C + D merge |

## The 5 hours

| Time | A · Model | B · Rules/data | C · UI | D · Story |
|---|---|---|---|---|
| **0:00–0:30** | Push code to GitHub. Run CLI on 3 samples. Fix env issues. | Collect 5–10 real spam screenshots from team phones, blur, label | `python app.py`, check upload works | README: fill model, hardware, team |
| **0:30–1:30** | Text-only eval (`--runs 1`). Note misses. | Add missing rules for real samples | Polish verdict card, Hindi section | Draft pitch from `07_PITCH_AND_DEMO.md` |
| **1:30–2:30** | Tune prompt / add 1–2 few-shots for misses | Tune regex; zero false-criticals | Add example buttons for the 3 best demo shots | Make 4–5 slides |
| **2:30–3:30** | Image eval on 10 samples; check OCR quality; decide E4B vs E2B | Review `eval_runs.csv` with A | Record a 60-sec backup demo video | DEV post draft (optional bonus) |
| **3:30–4:15** | 🔒 **Code freeze.** Run full eval: 30 × 3 | Help D with the results table | Rehearse live demo twice | Paste `EVAL_REPORT.md` into README |
| **4:15–5:00** | Final push, tag `v1.0` | Submit on MLH for **every eligible track** | Final rehearsal | Pitch rehearsal with timer |

**Rule: if something isn't working by its time slot, cut it.** A working core demo beats a broken extra feature.

## Fallback plans

| Problem | Do this |
|---|---|
| E4B too slow / out of memory | `KAVACH_MODEL=gemma4:e2b` everywhere; report both if time allows |
| OCR misreads screenshots | Demo with pasted text too; mention OCR quality honestly; crop images tighter |
| Ollama rejects `think` field | Already handled (auto-retry without it). Or set `KAVACH_THINK=false`. |
| Model outputs odd verdicts | Add one few-shot example of that exact case in `prompts.py` |
| Gradio breaks | Demo via CLI in terminal: `python -m kavach.cli --image ... --brief` |
| No GPU | Use E2B; run eval with `--text-only`; show 2–3 image runs live |
| Laptop dies during demo | Play the backup video |

## Stretch goals (only after the core is done and measured)

1. **Batch mode:** check a whole folder of screenshots (`for f in folder/*.png`).
2. **Telegram bot:** forward a screenshot to a bot running on the laptop (still local inference).
3. **Hindi Devanagari test images** to show Indic OCR.
4. **Sarvam Edge / local TTS** to read the verdict aloud for elderly users.
5. **Raspberry Pi 5** build for the Physical AI track (see `09_EDGE_RASPBERRY_PI.md`).
