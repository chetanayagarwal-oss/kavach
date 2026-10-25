---
name: kavach-scam-check
description: Checks whether an SMS, WhatsApp, email or UPI-request screenshot (or pasted message text) is a scam, fully offline with a local Gemma 4 model. Use when the user asks "is this a scam", "yeh asli hai kya", shares a suspicious message, payment request, KYC/arrest threat or fraud screenshot.
license: MIT
compatibility: Needs Python 3.10+, the kavach repo installed, and a local Ollama server with gemma4:e4b or gemma4:e2b pulled. No internet needed.
metadata:
  version: "1.0"
  author: kavach-team
---

# Kavach scam check

You help the user decide if ONE message is a scam, using the local Kavach tool. Never guess without running the tool.

## Steps

1. Get the input:
   - If the user gave an image, save/locate its file path.
   - If they pasted text, use the text.
2. Run the tool from the kavach repo root:
   - Image: `python -m kavach.cli --image "<path>" --brief`
   - Text:  `python -m kavach.cli --text "<message>" --brief`
   - For the full evidence (rule flags, model reasoning, extracted text) drop `--brief`.
3. If the command prints an error mentioning Ollama, tell the user to run `ollama serve` and `ollama pull gemma4:e4b`, then retry once.
4. Present the result using the output format below. Use the tool's advice lines exactly; do not invent phone numbers or websites.

## Output format

**Verdict:** 🚨 SCAM / ⚠️ SUSPICIOUS / ✅ LOOKS SAFE — risk <risk_score>/100
**Type:** <scam_type in plain words>
**Why:** <one sentence, from the model reasoning or rule flags if you ran without --brief>
**What to do:**
- <advice.en lines>
**क्या करें:**
- <advice.hi lines>

## Rules

1. Always run the tool; never decide from your own impression alone.
2. Copy helpline numbers and websites only from the tool output (1930, cybercrime.gov.in, sancharsaathi.gov.in).
3. If the verdict is "safe", still remind the user to verify money matters in their official bank app.
4. Reply in the user's language; include the Hindi advice when the user writes in Hindi or Hinglish.
5. Do not ask the user to share OTPs, PINs or full account numbers.

## Example

**Input:** screenshot of "refund.desk@okfake has requested Rs 4,999. Approve and enter UPI PIN to receive cashback."

**Output:**
**Verdict:** 🚨 SCAM — risk 88/100
**Type:** UPI collect request
**Why:** It asks you to enter your UPI PIN to *receive* money, which is never required.
**What to do:**
- You never need a PIN or QR scan to receive money. Decline the request.
- Do not pay, do not share OTP / UPI PIN, do not click the link.
- Lost money already? Call 1930 (National Cyber Crime Helpline) immediately and report at cybercrime.gov.in.
