# 01 · The idea

## One line

**Kavach is an offline, single-task AI agent that tells you if a message screenshot is a scam — running on a 4.5B open model on your own laptop.**

## The user

Think of three people:

| Person | Situation | What they need |
|---|---|---|
| Nani (65) in Pali | Gets a WhatsApp "video call from CBI" | A clear "this is a scam, cut the call" in Hindi |
| A college student | Sells a cycle on OLX, buyer sends "I paid extra, return it" screenshot | Instant check before handing over money |
| A small shop owner | Customer shows a "payment successful" screen | Reminder to check the bank app, not the screenshot |

Common need: **paste or snap → get a trustworthy answer in seconds, without sending private chats to the cloud.**

## Why offline matters (judges will ask)

- **Privacy.** Screenshots contain names, numbers, bank details. They never leave the device.
- **Trust.** A fraud checker that uploads your messages is itself a risk.
- **Reach.** Works on weak networks and old laptops; the E2B model even runs on a Raspberry Pi 5.
- **Track rules.** The Local Agentic track forbids hosted model APIs. Offline is the requirement, not a gimmick.

## Why this idea scores well

| What judges reward (from past Gemma winners) | How Kavach does it |
|---|---|
| Real, local problem with clear users | Indian UPI / digital-arrest fraud, Hindi output |
| Offline / on-device | Gemma 4 via Ollama, zero cloud calls |
| Photo or voice input instead of typing | Screenshot in, verdict out |
| Deterministic guardrails for critical output | Rule checker + fixed advice templates |
| Measured, honest numbers | 30 samples × 3 runs, accuracy, consistency, tok/s |

## Track mapping (one project, up to four tracks)

| Track | Fit | What to show |
|---|---|---|
| **Best Local Agentic Tool** | ★★★ main target | One task, local only, 3-run eval table, model + params + hardware in README |
| **Best Use of Gemma 4** | ★★★ | Gemma's vision reads the screenshot; native structured output |
| **Best Open-Source AI Project** | ★★☆ | MIT repo + reusable Agent Skill (`SKILL.md`) other agents can call |
| **Physical AI / Edge** | ★☆☆ optional | Only if a Pi 5 is available: E2B + camera, see `09_EDGE_RASPBERRY_PI.md` |

## What makes it "deep tech" (not just an API wrapper)

1. **Grammar-constrained decoding** with JSON schemas — reliability at the token level.
2. **Neuro-symbolic fusion** — a weighted mix of model judgement and deterministic rules, with hard overrides for critical signals.
3. **Two-stage perception → reasoning** — OCR first, then judgement on clean text, so each step can be tested on its own.
4. **Reliability engineering** — repeated-run consistency measured and reported, not just claimed.

## Scope guard (what we will NOT build today)

- ❌ A general chatbot ("ask me anything about fraud")
- ❌ Voice-call recording / live call analysis
- ❌ A mobile app (Gradio web UI on the laptop is enough for the demo)
- ❌ Fine-tuning (no time; few-shot + schema + rules is enough)

These go into "future work" in the pitch.
