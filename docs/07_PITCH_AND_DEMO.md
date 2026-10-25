# 07 · Pitch and demo

## 3-minute pitch script

**[0:00–0:25] Hook**
> "Raise your hand if a relative has forwarded you a message asking *'yeh asli hai kya?'*
> In the first half of 2026, Indians filed over 12 lakh cyber-fraud complaints and reported more than ₹10,000 crore lost.
> And the usual defence is still: send the screenshot to a smarter friend."

**[0:25–0:45] Solution**
> "Kavach is that friend. Drop in a screenshot — SMS, WhatsApp, UPI request — and in seconds you get:
> scam or safe, why, and what to do, in English and Hindi.
> And it runs completely on this laptop. Your private messages never go to any server."

**[0:45–1:45] Live demo** (see below)

**[1:45–2:30] How it works / why it's reliable**
> "Under the hood: Gemma 4 E4B, a 4.5-billion-parameter open model, running locally in Ollama.
> Three things make a small model trustworthy:
> One — grammar-constrained decoding: the model can only output valid JSON with our allowed labels.
> Two — a deterministic rule engine for the signals that should never be missed, like asking for your OTP.
> Three — the model never writes helpline numbers; those come from fixed templates."

**[2:30–2:50] Proof**
> "We tested 30 screenshots, three times each. Accuracy 100%, scam recall 100%, 0 false positives out of 12,
> and 100% consistent answers across all three runs, at 54 tokens per second."

**[2:50–3:00] Close**
> "It's MIT-licensed and also ships as an Agent Skill, so Hermes, Claude Code or Codex can use it as a tool.
> Kavach — screenshot daalo, sach jaano. Thank you."

## Demo script (exact clicks)

Warm the model first (run one check before you go on stage).

1. **Digital arrest** (`s01.png`) → 🚨 SCAM, type digital arrest, Hindi advice, 1930. *"The rule engine caught the CBI + video call pattern."*
2. **UPI collect trick** (`s03.png`) → 🚨 SCAM. *"You never need a PIN to receive money — Kavach knows that."*
3. **Real OTP message** (`g01.png`) → ✅ SAFE. *"It's not paranoid: a normal bank OTP that says 'don't share' passes."*
4. **Wildcard:** ask a judge for a message from their own phone, or paste one. *(Huge credibility if it works. Skip if nervous.)*
5. Point at the footer: model name, tok/s, "no internet used". Optional: turn WiFi off before step 1 to prove it.

## Slides (5 max)

1. Title + one-line problem + the ₹10,000 crore stat
2. Demo screenshot of the verdict card (backup if live fails)
3. Architecture diagram (from `03_ARCHITECTURE.md`)
4. Eval table: accuracy, recall, FP, consistency, tok/s, model, hardware
5. Tracks + open source + future work (Telegram bot, Pi 5, real dataset, more languages)

## Judge Q&A — prepare these answers

| Question | Answer |
|---|---|
| "Why not just use GPT / Gemini API?" | Privacy (messages stay on device), works offline, and the track requires local inference. Also no per-request cost. |
| "How do you know it's accurate?" | 30 labelled samples × 3 runs, every prediction saved in `eval_runs.csv`. Small set — we say that openly. |
| "What if scammers change wording?" | The model generalises beyond regex; rules only add guaranteed signals. New patterns → one rule or one few-shot example. |
| "False positives?" | We test tricky safe messages (OTP, bank credit, bill). FP rate 0/12. A "suspicious" level exists for unclear cases. |
| "Why Gemma over Qwen?" | Gemma's vision is strong at reading documents and filling strict schemas — exactly this task. Qwen is often better at code, which we don't need here. |
| "Is this deep tech?" | Constrained decoding, neuro-symbolic fusion with hard overrides, measured run-to-run reliability, two-stage perception → reasoning. |
| "Why not fine-tune?" | 5 hours. Few-shot + schema + rules got us 100% accuracy. Fine-tuning E2B with Unsloth on a real dataset is the next step. |
| "Can it run on a phone?" | E2B runs on Raspberry Pi 5 class hardware; Android via LiteRT-LM is the next step. |
| "Who would use it?" | Families (elders), small sellers, bank/telco helpdesks as a triage tool, cyber-cell awareness drives. |

## DEV post (bonus, 20 minutes)

Title idea: *"Kavach: an offline scam checker on a 4.5B Gemma 4 model — and how grammar-constrained decoding made it reliable."*
Sections: problem → demo GIF → architecture → eval table → what we learned. Tag `#hacktoberfest #hf26challenge #gemma`.
