# 02 · Research: event, sponsors, competitors, past winners

All facts paraphrased from the sources linked at the bottom (checked 25 Oct 2026).

## The event

- **Hacktoberfest Hack Day Jaipur × Hack IT Sapiens**, LNMIIT Jaipur, Sun 25 Oct 2026, 10:00–17:00 IST.
- **5 hours of hacking**, teams of 2–4, every member registers separately.
- Theme: working prototypes with **open-source / open-weight AI at the core**, any problem domain.
- Resources the organizers linked: Gemma 4 guides, Sarvam AI docs, Graphify, Hermes Agent, Agent Skills.

### The four tracks — exact requirements

| Track | Sponsor | Key rules |
|---|---|---|
| Best Use of Gemma 4 | Google DeepMind | Multimodal (text + images), focused tool for learning / productivity / community |
| Best Open-Source AI Project | DigitalOcean | Open-source or open-weight AI must be central: agent skill, open model, or open harness |
| Best Local Agentic Tool | Event prize | Local inference only; open model; one task; public repo + license; state model, params, min hardware; **3 repeated runs**; scored on success rate, reliability, usefulness; **tok/s is the tie-breaker** |
| Physical AI | Event prize | Inference fully offline on a separate device (Pi, ESP32…); open model used meaningfully; public repo; working prototype |

**Important catch:** the organizers note Sarvam's APIs are hosted, so they **cannot** be the core engine for the local track. Gemma via Ollama is.

## Sponsors and the ecosystem

### Google DeepMind — Gemma 4
- Sizes: **E2B** (~2.3B effective), **E4B** (~4.5B effective), **26B MoE** (~3.8B active), **31B dense**.
- All support vision and native function calling; E2B/E4B also take audio; built-in thinking mode; **Apache 2.0** license.
- Rough VRAM: E2B 4–6 GB (or CPU with 8 GB RAM), E4B 6–8 GB, 26B MoE 8–12 GB, 31B 16–20 GB.
- Google's push: on-device / edge. Runtimes they highlight: LiteRT, Ollama, llama.cpp, Cactus, Unsloth.
- On a Raspberry Pi 5 (8 GB), LiteRT-LM runs E2B at about 9 tok/s decode vs about 4 tok/s with llama.cpp.

**Competitors:** Qwen 3.6 (Alibaba), Llama (Meta), Mistral, gpt-oss.
**Community view (r/LocalLLaMA, HN):** Qwen is often preferred for coding and tool calling; Gemma is often preferred for documents, OCR and precise structured extraction. → **Kavach uses Gemma for exactly its strength: reading a screenshot and filling a strict schema.**

### DigitalOcean — Hacktoberfest presenting partner
- Hacktoberfest 2026 is run by MLH + DEV with DigitalOcean and **dropped PR-counting**; the focus is building with open-source AI (skills.md files, agents, fine-tuning open models).
- Product: Gradient AI / Inference Engine — serverless, OpenAI-compatible inference over open and frontier models, plus GPU Droplets.
- Competitors: AWS Bedrock, Together AI, Fireworks, RunPod.
- DEV runs weekly Hacktoberfest challenges + a "Best Use of DigitalOcean" category → a DEV write-up of Kavach is a bonus entry.

### Sarvam AI (resource)
- Open-sourced Sarvam 30B and 105B (MoE, Apache 2.0), trained in India; on Artificial Analysis they trail similar-size Qwen/GLM/gpt-oss models.
- Also has Sarvam Edge (offline speech/translation). Good for an Indic stretch goal, not the core.

### Graphify (resource)
- Turns a codebase into a local knowledge graph (tree-sitter, no LLM); ~134k GitHub stars, YC-backed.
- Signals the organizers like **agent tooling and skills**.

### Nous Research — Hermes Agent (resource)
- Open-source self-improving agent framework; ~140k stars within months of a Feb 2026 release.
- Competitors: OpenClaw, GoClaw, LangGraph, CrewAI. Uses the agentskills.io skill format → Kavach's `SKILL.md` plugs straight in.

### Agent Skills (open standard)
- A skill = a folder with `SKILL.md` (YAML front-matter + instructions), loaded on demand.
- Supported by Codex, Copilot, VS Code, Cursor, Goose and more. Especially useful for small local models, which need explicit structure.

## Past winners — what actually wins

### Gemma 4 Good Challenge (Kaggle, 1,600+ submissions, results Aug 2026)

| Winner | What | Lesson for us |
|---|---|---|
| GEM-4 (1st) | Wearable robot assistant, fine-tuned E2B controller | Physical + edge impresses |
| Trido (2nd) | Voice whiteboard for teachers on budget laptops, offline fallback | Empathy + offline |
| CodeBuddy | Photo of handwritten Python → E4B transcribes & debugs offline | **Snap a photo → instant help** = our UX |
| TrueVoice | Detects voice-clone scams on the edge with E4B audio | **Fraud/safety is a prize category judges value** |
| Project Rosie | Agentic vet-oncology assistant with deterministic templates for critical specs | **Templates for critical output** = our advice module |
| Acuífero·Vigía | Offline flood warnings with auditable reasoning on Pi 5 | Show the evidence trail |
| PreVillage | WhatsApp voice navigator for Nepal govt services, llama.cpp on Pi 5 at 7.5 tok/s | Local language + Pi works |
| KawanIsyarat | Sign-language assistant; disabled thinking mode for real-time speed | **Turn thinking off for tok/s** |
| MindBridge | Hindi-dialect mental-health screening, fine-tuned E2B audio | Hindi-first projects win |

### DEV Gemma 4 Challenge winners (June 2026)
- Offline disaster companion (Philippines), visual interpreter for the blind, P2P inference network,
  **an offline phone-control agent where a 2B model goes through a strict tool dispatcher**, and a local HIPAA-safe Postgres co-pilot.
- Pattern: **small model + strict structure = trustworthy agent**.

## The problem — numbers to quote in the pitch

- Jan–Jun 2026: **12.7 lakh+** cyber-fraud complaints, **₹10,178 crore+** reported losses (PSU Connect summary).
- UPI frauds: ₹1,087 crore in FY24, ₹981 crore in FY25, ₹805 crore in FY26 till November (Govt reply in Lok Sabha).
- "Digital arrest" is not a legal concept in India; no agency asks for money or details over video calls.

## The technique — evidence that constrained decoding helps

- NVIDIA's AI Red Team ran 13 small models on 299 Bash tasks: grammar-constrained decoding lifted the average pass rate from **62.5% to 75.2%**.
- Recommended pattern: let the model reason in a free-text field first, constrain the final answer. (Kavach's schema puts `reasoning` before `verdict` for this reason.)

## Sources

- Event: https://events.mlh.com/events/15448-hacktoberfest-hack-day-jaipur-x-hack-it-sapiens
- Tracks: https://www.mlh.com/events/hacktoberfest-hack-day-jaipur-x-hack-it-sapiens
- Gemma 4 sizes: https://dev.to/purpledoubled/how-to-run-googles-gemma-4-locally-with-ollama-all-4-model-sizes-compared-2pbh
- Gemma on Pi 5: https://blog.circuit.rocks/?p=6963
- Gemma 4 Good winners: https://blog.google/innovation-and-ai/technology/developers-tools/winning-entries-gemma-4-good-challenge/
- DEV Gemma 4 winners: https://dev.to/devteam/congrats-to-the-gemma-4-challenge-winners-4fgc
- Hacktoberfest FAQ: https://hacktoberfest.com/questions/
- DEV HF26 challenges: https://dev.to/challenges/hf26
- DigitalOcean inference: https://www.digitalocean.com/blog/whats-new-on-gradient-ai-platform
- Sarvam benchmarks: https://artificialanalysis.ai/articles/sarvam-105b-Sarvam-30b-everything-you-need-to-know
- Gemma vs Qwen (Reddit): https://reddit.sentinel-team.org/posts/1uvl312/snapshots/2026-07-17T18%3A53%3A30.39359Z
- Gemma vs Qwen (HN): https://brianlovin.com/hn/47960507
- Hermes Agent: https://dev.to/truongpx396/hermes-agent-the-self-improving-agent-framework-and-how-it-compares-to-openclaw-goclaw-22mc
- Graphify: https://github.com/Graphify-Labs/graphify
- Agent Skills: https://dev.to/loc_carrre_0d798813c662/agent-skills-explained-what-they-are-what-they-arent-and-how-to-use-them-bf9
- NVIDIA constrained decoding: https://developer.nvidia.com/blog/improving-bash-generation-in-small-language-models-with-grammar-constrained-decoding/
- Fraud stats 2026: https://www.psuconnect.in/articles/online-fraud-in-india-2026-common-scams-real-risks-how-to-stay-safe
- UPI fraud (Lok Sabha): https://madhyamamonline.com/amp/india/upi-linked-frauds-amount-to-rs-805-crore-far-fy26-govt-1477281
