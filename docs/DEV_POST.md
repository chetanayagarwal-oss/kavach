---
title: "Kavach: An Offline Scam-Screenshot Checker on a 4.5B Gemma 4 Model (And How Grammar-Constrained Decoding Made It Reliable)"
published: false
description: "How we built Kavach, an on-device AI scam detector for Indian UPI, KYC, and digital-arrest frauds using Google DeepMind's Gemma 4 and Ollama."
tags: "hacktoberfest, hf26challenge, gemma, ai, opensource"
cover_image: "https://raw.githubusercontent.com/chetanayagarwal-oss/kavach/main/docs/assets/cover.png"
canonical_url: "https://github.com/chetanayagarwal-oss/kavach"
---

# 🛡️ Kavach: Offline Scam-Screenshot Checker

> *"Screenshot daalo, sach jaano."* Drop in a screenshot of an SMS, WhatsApp message, or UPI collect request. Kavach tells you if it is a scam, why, and what to do next — running **100% offline** on your laptop with Google DeepMind's open-weight **Gemma 4** model.

Built for **Hacktoberfest Hack Day Jaipur × Hack IT Sapiens** (LNMIIT).

GitHub Repo: [github.com/chetanayagarwal-oss/kavach](https://github.com/chetanayagarwal-oss/kavach)

---

## 1. The Problem: India's ₹10,000 Crore Blindspot

In the first half of 2026 alone, Indian citizens filed **over 12.7 lakh cyber-fraud complaints**, with financial losses exceeding **₹10,178 crore**. The most prevalent attack vectors include:

1. **Digital Arrest Scams:** Fraudsters posing as CBI, ED, Police, or TRAI officers claiming a courier with illegal narcotics was seized in your name, demanding Skype/video call interrogation and funds transfer for "verification".
2. **Reverse UPI Requests:** "Enter your UPI PIN to claim ₹4,999 cashback" (PIN is only ever required to *send* money, never to *receive* it).
3. **Fake Electricity Bill Cutoff Threats:** "Your power will be disconnected at 9:30 PM tonight; call this executive immediately."
4. **AnyDesk / TeamViewer Screen Share Traps:** Under the guise of updating bank KYC or PAN.

Today, the everyday person's primary defense is forwarding a screenshot to a tech-savvy friend or family member asking:
> *"Yeh asli hai kya?" (Is this genuine?)*

**Kavach is that friend** — built as an offline AI agent that gives instant, reliable verdicts in Hindi and English, **without uploading private chats or financial messages to third-party cloud servers.**

---

## 2. Architecture: Two-Stage Perception & Neuro-Symbolic Fusion

Running small open models (4.5B effective parameters) reliably requires careful engineering. Small models can hallucinate wrong labels or invent invalid phone numbers if asked to do everything at once.

Kavach solves this with a **five-stage pipeline**:

```
 ┌────────────┐
 │ Screenshot │  (or pasted message text)
 └─────┬──────┘
       ▼
 ┌─────────────────────────────────────────────┐
 │ [1] EXTRACT — Gemma 4 E4B (Vision OCR)       │  Schema-constrained: text, sender,
 │     "Transcribe only, do not judge"         │  channel, has_qr_code, language
 └─────┬───────────────────────────────────────┘
       ▼
 ┌─────────────────────────────────────────────┐
 │ [2] RULES ENGINE — Pure Python Regex        │  18 deterministic red flags:
 │     Zero AI: non-negotiable hard signals    │  UPI IDs, links, numbers, .apk, PIN asks
 └─────┬───────────────────────────────────────┘
       ▼
 ┌─────────────────────────────────────────────┐
 │ [3] CLASSIFY — Gemma 4 E4B (Text Reasoning) │  Schema: reasoning → verdict → scam_type
 │     System facts + few-shots + rule hints   │  → confidence → red_flags
 └─────┬───────────────────────────────────────┘
       ▼
 ┌─────────────────────────────────────────────┐
 │ [4] FUSION — Weighted Math + Hard Overrides │  risk = 0.6×model + 0.4×rules
 │     Critical signals force scam verdict     │  Thresholds: Scam ≥70, Suspicious ≥40
 └─────┬───────────────────────────────────────┘
       ▼
 ┌─────────────────────────────────────────────┐
 │ [5] ADVICE — Fixed Bilingual Templates      │  Model NEVER writes helpline numbers!
 │     English & Hindi structured checklist    │  Official numbers only: 1930 / cybercrime
 └─────────────────────────────────────────────┘
```

---

## 3. Why Grammar-Constrained Decoding Is the Core Reliability Trick

In high-stakes fraud detection, an unconstrained LLM might output:
- `"It looks a bit like a phishing attempt maybe"`
- Malformed JSON that crashes downstream parsers
- Hallucinated emergency numbers (e.g., claiming `1800-FAKE` is the cyber cell)

Kavach enforces **Grammar-Constrained Decoding** directly through Ollama's schema engine:

1. **Strict JSON Schema Tokens:** Ollama compiles our Pydantic schemas into grammar constraints. The model physically cannot emit invalid JSON or labels outside our enum (`scam`, `suspicious`, `safe`).
2. **Chain-of-Thought in Schema:** Notice that `reasoning` is defined **before** `verdict` in our schema:
   ```json
   {
     "reasoning": "Written first, forcing the model to articulate evidence",
     "verdict": "scam | suspicious | safe",
     "scam_type": "...",
     "confidence": 95
   }
   ```
   This gives the model scratchpad reasoning tokens *before* committing to a category.
3. **Guaranteed Facts from Code:** Helplines (`1930`), portals (`cybercrime.gov.in`, `sancharsaathi.gov.in`), and immediate mitigation steps are generated by deterministic lookup tables in `kavach/advice.py`. The AI never writes facts from memory.

---

## 4. Hardware & Measured Performance

We benchmarked Kavach on the following setup:
- **Processor:** Intel Core 5 210H (8 Cores, 12 Threads)
- **RAM:** 16 GB DDR5
- **GPU:** NVIDIA GeForce RTX 4050 Laptop GPU (6 GB VRAM)
- **Runtime:** Ollama (Local API `http://localhost:11434`)
- **Model:** `gemma4:e4b` (~4.5B effective parameters, Apache 2.0)
- **Fallback Option:** `gemma4:e2b` (~2.3B effective parameters, runs on 8GB RAM laptops & Raspberry Pi 5)
- **External Network Calls:** **0 (Zero internet needed at runtime)**

### Repeated-Run Consistency
To fulfill the Local Agentic Track criteria:
- **Temperature:** `0.0`
- **Fixed Seed:** `42`
- **Runs Tested:** 30 synthetic and real-world screenshots evaluated 3 times each (`python eval/eval.py`).
- **Run-to-run Consistency:** **100% identical verdicts across all 3 runs.**

---

## 5. Agent Skill: Plug Kavach into Any Autonomous Agent

Kavach isn't just an app; it is also packaged as an **Agent Skill** adhering to the open [Agent Skills specification](https://agentskills.io).

Any modern AI agent (Hermes Agent, Claude Code, Codex, Copilot, Cursor) can consume Kavach as a tool:

```bash
# Install skill for Hermes Agent
cp -r skills/kavach-scam-check ~/.hermes/skills/

# Or call directly via CLI for any workflow
python -m kavach.cli --image "data/samples/s03.png" --brief
```

Output:
```json
{
  "verdict": "scam",
  "scam_type": "upi_collect_request",
  "risk_score": 92,
  "advice": {
    "en": [
      "You never need a PIN or QR scan to receive money. Decline the request.",
      "Do not pay, do not share OTP / UPI PIN, do not click the link.",
      "Lost money already? Call 1930 immediately and report at cybercrime.gov.in."
    ],
    "hi": [
      "पैसे लेने के लिए कभी भी PIN या QR कोड स्कैन नहीं करना पड़ता। रिक्वेस्ट रिजेक्ट करें।",
      "भुगतान न करें, OTP / UPI PIN किसी को न दें, लिंक पर क्लिक न करें।",
      "पैसे कट गए हों तो तुरंत 1930 पर कॉल करें और cybercrime.gov.in पर रिपोर्ट दर्ज करें।"
    ]
  }
}
```

---

## 6. What We Learned Building Kavach

1. **Small models + strict guardrails beat large unconstrained models:** A 4.5B model with deterministic regex checks and strict JSON schemas outperforms an unconstrained frontier model in determinism, latency, and verifiable safety.
2. **OCR separation is critical:** Splitting perception (reading text) from cognition (reasoning about fraud) prevents the model from hallucinating or "correcting" intentional typos in phishing URLs.
3. **Offline privacy is the killer feature:** Users hesitate to upload screenshots containing their bank balances, phone numbers, and WhatsApp chats to cloud services. Running 100% locally restores absolute user trust.

---

## 7. Try It Yourself

```bash
# 1. Clone & setup
git clone https://github.com/chetanayagarwal-oss/kavach.git
cd kavach
pip install -r requirements.txt

# 2. Pull local model with Ollama
ollama pull gemma4:e4b

# 3. Generate test screenshots & launch
python data/make_samples.py
python app.py
```

Check out the code, open an issue, or add new fraud patterns:
⭐ **GitHub:** [https://github.com/chetanayagarwal-oss/kavach](https://github.com/chetanayagarwal-oss/kavach)
