# 03 · Architecture

## The pipeline

```
 ┌────────────┐
 │ Screenshot │  (or pasted text → skips step 1)
 └─────┬──────┘
       ▼
 ┌─────────────────────────────────────────────┐
 │ [1] EXTRACT  — Gemma 4 E4B (vision)          │  schema: message_text, sender,
 │     "transcribe only, don't judge"           │          channel, has_qr_code, language
 └─────┬───────────────────────────────────────┘
       ▼
 ┌─────────────────────────────────────────────┐
 │ [2] RULES — pure Python regex, no AI         │  → flags (with evidence) + score 0-100
 │     OTP/PIN asks, digital arrest, AnyDesk,   │  → entities: UPI IDs, links, phones, ₹
 │     short links, fake domains, .apk, ...     │
 └─────┬───────────────────────────────────────┘
       ▼
 ┌─────────────────────────────────────────────┐
 │ [3] CLASSIFY — Gemma 4 E4B (text)            │  schema: reasoning → verdict → scam_type
 │     system rules + 2 few-shot + RULE_FLAGS   │          → confidence → red_flags
 └─────┬───────────────────────────────────────┘
       ▼
 ┌─────────────────────────────────────────────┐
 │ [4] FUSE — weighted score + hard overrides   │  → final verdict + risk 0-100
 └─────┬───────────────────────────────────────┘
       ▼
 ┌─────────────────────────────────────────────┐
 │ [5] ADVICE — fixed EN/HI templates           │  model never writes numbers or steps
 └─────────────────────────────────────────────┘
```

Code map: `kavach/pipeline.py` (steps 1, 3, 4), `kavach/rules.py` (2), `kavach/advice.py` (5).

## Design decisions (and why) — simple words mein

| Decision | Why |
|---|---|
| **Two model calls (extract, then classify)** instead of one | Each step is easy to test alone. If the verdict is wrong you can see whether OCR or reasoning failed. Classification on clean text is also more stable. |
| **JSON schema on every call** (Ollama `format`) | Ollama converts the schema to a grammar. The model can only pick valid tokens → zero broken JSON, zero invented labels. This is the core reliability trick. |
| **`reasoning` field first in the schema** | The model "thinks" in a short sentence before committing to a verdict, but the verdict itself is still forced into the allowed list. |
| **Thinking mode OFF** | Fewer tokens, faster answers, better tok/s tie-breaker. The few-shot + rules give enough structure. |
| **Temperature 0 + seed 42** | Same input → same output. That is what "3 repeated runs, consistent output" checks. |
| **Regex rules alongside the model** | Small models can miss obvious signals. Rules never do, and they produce evidence the judges can read. |
| **Rule flags fed to the model as hints** | The model gets a second opinion; it can still disagree (e.g. "do not share OTP" is safe). |
| **Advice from templates** | Helpline numbers and steps are facts. Facts come from code, not from a 4B model. |
| **Ollama** as runtime | One command install, OpenAI-style API, handles images + schemas. Swap to llama.cpp later if needed. |

## Fusion math

```
model_risk = scam        → 50 + confidence/2        (50..100)
             suspicious  → 35 + 0.3 × confidence    (35..65)
             safe        → 0.35 × (100 − confidence) (0..35)

risk = 0.6 × model_risk + 0.4 × rule_score

if any CRITICAL rule fired  → risk = max(risk, 75)      # OTP/PIN ask, PIN-to-receive,
                                                        # digital arrest, AnyDesk, .apk link
if model says scam with confidence ≥ 85 → risk = max(risk, 70)

risk ≥ 70 → SCAM      40–69 → SUSPICIOUS      < 40 → SAFE
```

All weights and thresholds live in `kavach/config.py` and can be changed with env vars
(`KAVACH_MODEL_WEIGHT`, `KAVACH_SCAM_THRESHOLD`, `KAVACH_SUSPICIOUS_THRESHOLD`). Tune them on the eval set, not by feel.

**Example.** Model says `safe` with 90% confidence (risk 3.5), rules found nothing (0) → risk 2 → SAFE.
Model says `suspicious` 60% (risk 53) and rules found urgency + KYC + fake domain (60) → 0.6×53 + 0.4×60 = 55.8 → SUSPICIOUS.
Same message but it also asks for the OTP (critical) → forced to 75 → SCAM.

## Output contract (what `check()` returns)

```json
{
  "verdict": "scam | suspicious | safe",
  "risk_score": 0,
  "scam_type": "kyc_update",
  "model":   {"verdict": "...", "confidence": 0, "reasoning": "...", "red_flags": ["..."]},
  "rules":   {"flags": [{"id": "...", "label_en": "...", "label_hi": "...", "weight": 0, "evidence": "...", "critical": false}],
              "urls": [], "upi_ids": [], "phones": [], "amounts": [], "score": 0, "has_critical": false},
  "extracted": {"message_text": "...", "sender": "...", "channel": "sms", "has_qr_code": false, "language": "english"},
  "advice":  {"en": ["..."], "hi": ["..."]},
  "perf":    {"model_name": "gemma4:e4b", "total_s": 0.0, "output_tokens": 0, "decode_tok_s": 0.0, "calls": []}
}
```

## Speed tips (for the tok/s tie-breaker)

1. Keep thinking off (`KAVACH_THINK=false`, default).
2. Keep `num_ctx` small (4096 is plenty for one message).
3. Schemas shorten output: `red_flags` max 5, reasoning 2–3 sentences.
4. Warm the model before the demo: run one check so weights are already in memory.
5. If the laptop is slow, switch to `KAVACH_MODEL=gemma4:e2b` and re-run the eval to report both.
6. Pasted text skips the OCR call entirely (one model call instead of two).

## Where each sponsor technology sits

| Layer | Tech |
|---|---|
| Model | Gemma 4 E4B / E2B (open weights, Apache 2.0) |
| Runtime | Ollama (local); llama.cpp / LiteRT-LM on Pi 5 |
| Agent interface | `SKILL.md` (Agent Skills standard) + JSON CLI |
| Optional deploy | Public demo of the UI on a DigitalOcean GPU Droplet running the same open model (never a hosted frontier API) |
