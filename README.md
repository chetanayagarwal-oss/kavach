# 🛡️ Kavach — offline scam-screenshot checker

> **Screenshot daalo, sach jaano.** Drop in a screenshot of an SMS, WhatsApp message or UPI request.
> Kavach tells you if it is a scam, why, and what to do next, in English and Hindi.
> It runs **entirely on your own laptop** with Google's open-weight **Gemma 4** model. No internet, no cloud API.

Built at **Hacktoberfest Hack Day Jaipur × Hack IT Sapiens** (LNMIIT, 25 Oct 2026).

---

## The problem

Indian phone users get a steady stream of "digital arrest" calls, fake KYC links, UPI collect requests
("enter PIN to receive cashback"), fake job tasks and "Mummy, new number, send money" messages.
In the first half of 2026 alone, India logged over 12.7 lakh cyber-fraud complaints with reported losses above ₹10,000 crore.

Most people's real defence today is forwarding the screenshot to a smarter friend and asking *"yeh asli hai kya?"*
Kavach is that friend, in a form that works offline, in Hindi, and never sends your private messages to a server.

## What it does (one task, done reliably)

**Input:** one screenshot (or pasted text).
**Output:** `scam` / `suspicious` / `safe` + scam type + red flags with evidence + fixed advice (1930 helpline, cybercrime.gov.in, Sanchar Saathi).

```
screenshot ─► Gemma 4 reads it (OCR, JSON schema)
                 ─► regex rule checker (deterministic red flags + UPI IDs, links, numbers)
                     ─► Gemma 4 judges (JSON schema, rule flags as hints)
                         ─► fuse model + rules ─► verdict ─► fixed advice template
```

Why it is reliable on a small local model:

1. **Grammar-constrained decoding.** Both model calls use a JSON schema, so the model physically cannot output broken JSON or an invented label.
2. **Rules + model.** Non-negotiable signals (asking for OTP/PIN, "enter PIN to receive", digital-arrest threats, AnyDesk, `.apk` links) are caught by deterministic code.
3. **The model never writes advice or phone numbers.** Advice comes from fixed templates, so it cannot hallucinate a wrong helpline.
4. **Deterministic settings.** Temperature 0, fixed seed, thinking mode off.

## Model and hardware (required by the Local Agentic track)

| Item | Value |
|---|---|
| Model | `gemma4:e4b` (Gemma 4 E4B, ~4.5B effective parameters, Apache 2.0) via Ollama |
| Alternative | `gemma4:e2b` (~2.3B effective) for 8 GB RAM laptops / Raspberry Pi 5 |
| Minimum hardware tested | Intel Core 5 210H, 16 GB RAM, NVIDIA GeForce RTX 4050 Laptop GPU (6 GB VRAM) |
| Internet needed at runtime | **No** |
| Hosted AI APIs used | **None** |

## Results (3 repeated runs)

_Run `python eval/eval.py` and paste `results/EVAL_REPORT.md` here._

| Run | Accuracy | Scam recall | False-positive rate | Tok/s |
|---|---|---|---|---|
| 1 | | | | |
| 2 | | | | |
| 3 | | | | |

**Consistency (same verdict in all 3 runs):** ___ %

## Quick start

```bash
# 1. Install Ollama (https://ollama.com) and pull the model (≈9.6 GB, do this on good WiFi)
ollama pull gemma4:e4b

# 2. Install Python deps
pip install -r requirements.txt

# 3. Make the synthetic test screenshots
python data/make_samples.py

# 4a. Try the CLI
python -m kavach.cli --image data/samples/s03.png --brief

# 4b. Or the web UI
python app.py          # open http://127.0.0.1:7860

# 5. Reliability eval: 30 samples x 3 runs
python eval/eval.py
```

Use the smaller model: `KAVACH_MODEL=gemma4:e2b python app.py`

## Use it from any AI agent (Agent Skill)

`skills/kavach-scam-check/SKILL.md` follows the open Agent Skills format, so Hermes Agent, Claude Code,
Codex, Copilot or Cursor can call Kavach as a tool. See [`docs/04_PROMPTS_AND_SCHEMA.md`](docs/04_PROMPTS_AND_SCHEMA.md).

## Project layout

```
kavach/
├── kavach/            # the package
│   ├── pipeline.py    # extract → rules → classify → fuse
│   ├── rules.py       # deterministic red-flag checker
│   ├── schema.py      # JSON schemas (constrained decoding)
│   ├── prompts.py     # system prompts + few-shot examples
│   ├── advice.py      # fixed EN/HI advice templates
│   ├── config.py      # all settings (env-overridable)
│   └── cli.py         # JSON CLI for agents
├── app.py             # Gradio demo
├── eval/eval.py       # N-run reliability eval → results/EVAL_REPORT.md
├── data/              # synthetic samples + labels.csv
├── skills/            # Agent Skill (SKILL.md)
└── docs/              # idea, research, architecture, plan, pitch
```

## Docs

| File | What's inside |
|---|---|
| [01_IDEA.md](docs/01_IDEA.md) | Problem, user, why this wins, track mapping |
| [02_RESEARCH.md](docs/02_RESEARCH.md) | Sponsors, competitors, past winners, sources |
| [03_ARCHITECTURE.md](docs/03_ARCHITECTURE.md) | Pipeline, design decisions, fusion math |
| [04_PROMPTS_AND_SCHEMA.md](docs/04_PROMPTS_AND_SCHEMA.md) | Prompts, schemas, rules, skill usage |
| [05_EVAL_PLAN.md](docs/05_EVAL_PLAN.md) | Dataset, metrics, how to run and report |
| [06_BUILD_PLAN.md](docs/06_BUILD_PLAN.md) | Pre-event checklist, 5-hour timeline, roles, fallbacks |
| [07_PITCH_AND_DEMO.md](docs/07_PITCH_AND_DEMO.md) | 3-minute pitch, demo script, judge Q&A |
| [08_SUBMISSION_CHECKLIST.md](docs/08_SUBMISSION_CHECKLIST.md) | Per-track requirements, ticked |
| [09_EDGE_RASPBERRY_PI.md](docs/09_EDGE_RASPBERRY_PI.md) | Optional Physical AI track on a Pi 5 |

## Limits (honest)

- It is an assistant, not a guarantee. A "safe" verdict does not mean you should skip checking in your official bank app.
- The synthetic test set is small (30 samples). Real-world accuracy needs a larger, real dataset.
- Hindi in Devanagari works through Gemma's vision; our test images are English/Hinglish.

## License

MIT — see [LICENSE](LICENSE).
