# 04 · Prompts, schemas, rules and the Agent Skill

Source of truth is the code; this file explains it so any teammate can tune it fast.

## 1. Extraction prompt (`EXTRACT_SYSTEM`)

Goal: **transcribe only**. No judging. Judging during OCR makes small models "fix" or skip suspicious text.

Key instructions:
- copy ALL text in reading order
- keep numbers, links, UPI IDs, amounts, Hindi/Hinglish exactly
- no translating, summarising or opinions

Schema (`EXTRACT_SCHEMA`): `message_text`, `sender`, `channel` (enum), `has_qr_code`, `language` (enum).

## 2. Classification prompt (`CLASSIFY_SYSTEM`)

Short list of **facts**, not vibes. Small models follow concrete rules much better than long essays:

- Police / CBI / ED / customs / courts never "digitally arrest" on video calls or ask money to close a case.
- You never need a UPI PIN or QR scan to **receive** money.
- Banks never ask for OTP / PIN / CVV / password. "Do not share OTP" messages are normal.
- Official domains (sbi.co.in, .gov.in). Short links, odd domains, `.apk` = red flags.
- Pressure, secrecy, remote-access apps = red flags.
- Pay-to-earn, guaranteed returns, unentered lotteries, "new number, send money" = classic scams.
- Delivery updates, credit alerts, official bill reminders, chats = safe.

Plus: rule flags are **hints, not proof**; `safe` ⇒ `scam_type = not_scam`.

### Few-shot (2 examples, one scam + one safe)

The safe example (a real-looking OTP message that says "do not share") teaches the model the most common false positive.
**If your eval shows a specific mistake repeating, add ONE example for it** — that is the highest-leverage fix.

### Schema (`CLASSIFY_SCHEMA`) — field order matters

```
reasoning   (string, 2-3 sentences)   ← written first = mini chain-of-thought
verdict     (enum: scam | suspicious | safe)
scam_type   (enum: 16 types, see schema.py)
confidence  (integer 0-100)
red_flags   (array of strings, max 5)
```

## 3. Scam types (16)

`digital_arrest`, `upi_collect_request`, `fake_payment_screenshot`, `kyc_update`, `otp_or_pin_request`,
`phishing_link`, `job_task_scam`, `investment_trading`, `lottery_prize`, `parcel_customs`, `electricity_bill`,
`loan_app`, `family_impersonation`, `remote_access`, `other_scam`, `not_scam`.

Each has its own EN + HI tip in `advice.py`.

## 4. Rule checker (`rules.py`)

| Rule id | Weight | Critical | Fires on (simplified) |
|---|---|---|---|
| `asks_secret` | 40 | ✅ | share/send/batao … OTP/PIN/CVV — **but not** if the text says "do not share" |
| `receive_needs_pin` | 40 | ✅ | receive/refund/cashback + enter PIN / scan QR / approve request |
| `digital_arrest` | 45 | ✅ | police/CBI/ED/customs/TRAI + video call / secrecy / arrest / warrant |
| `remote_access` | 40 | ✅ | AnyDesk, TeamViewer, QuickSupport, screen share |
| `apk_link` | 35 | ✅ | link ending in `.apk` |
| `authority_mention` | 15 | | authority word without coercion |
| `urgency` | 15 | | urgent, within 24 hrs, tonight, turant, jaldi, will be blocked |
| `kyc_block` | 20 | | KYC, PAN/Aadhaar update, account/SIM blocked |
| `lottery` | 30 | | lottery, lucky draw, KBC, you won |
| `job_task` | 30 | | part-time, work from home, like videos, Telegram task |
| `investment` | 30 | | guaranteed returns, % daily, paisa double |
| `electricity` | 30 | | power/bijli + disconnect/tonight |
| `parcel` | 30 | | parcel + seized/drugs/customs fee/redeliver fee |
| `family` | 30 | | new number/mummy/papa + money/emergency |
| `loan` | 25 | | instant/pre-approved loan, processing fee |
| `fake_payment` | 35 | | "payment successful" + "sent extra, return it" |
| `short_link` | 20 | | bit.ly, tinyurl, cutt.ly … |
| `suspicious_domain` | 25 | | brand word or risky TLD (.top/.xyz/.click…) on a non-official host |

Tested on the 30 synthetic samples: every scam gets ≥1 flag, no safe message gets a critical flag.

**Adding a rule** (2 minutes): write `def r_x(t) -> str` returning the matched evidence or `""`,
then add a line to `RULES`. Re-run `python eval/eval.py --text-only` to make sure false positives did not go up.

## 5. Agent Skill

`skills/kavach-scam-check/SKILL.md` lets any skills-compatible agent use Kavach:

```bash
# install into a project for agents that read .agents/skills (Codex, many others)
mkdir -p .agents/skills && cp -r skills/kavach-scam-check .agents/skills/

# Hermes Agent
cp -r skills/kavach-scam-check ~/.hermes/skills/

# Claude Code
mkdir -p .claude/skills && cp -r skills/kavach-scam-check .claude/skills/
```

The skill tells the agent to call `python -m kavach.cli --image <path> --brief` and how to present the JSON.
This is the "agent skill" artefact the Open-Source track explicitly mentions.

## 6. Tuning loop (use during hour 3)

1. `python eval/eval.py --text-only --runs 1` (fast, no OCR).
2. Open `results/eval_runs.csv`, sort by `correct`.
3. For each miss decide: **rule gap** (add/adjust regex) or **model gap** (add one few-shot example or one fact line).
4. Re-run. Stop when false positives are 0–1 and scam recall ≥ 90%.
5. Then run the full image eval `python eval/eval.py` for the final report.
