"""JSON schemas passed to Ollama's `format` field.

Ollama turns a JSON schema into a grammar, so the model can ONLY produce tokens
that keep the output valid. This is grammar-constrained decoding: no broken JSON,
no invented verdict labels, no retry loops.
"""

SCAM_TYPES = [
    "digital_arrest",          # fake police / CBI / ED / customs threatening arrest
    "upi_collect_request",     # "approve this request / enter PIN to receive money"
    "fake_payment_screenshot", # edited "payment successful" image sent to a seller
    "kyc_update",              # "your account / SIM will be blocked, update KYC"
    "otp_or_pin_request",      # asks you to share OTP / PIN / CVV
    "phishing_link",           # lookalike or shortened link to steal details
    "job_task_scam",           # part-time job, like videos, pay-to-earn tasks
    "investment_trading",      # guaranteed returns, trading tips, crypto doubling
    "lottery_prize",           # lottery, lucky draw, KBC prize
    "parcel_customs",          # parcel held with illegal items / customs fee
    "electricity_bill",        # power will be cut tonight, call this number
    "loan_app",                # instant loan, harassment, advance fee
    "family_impersonation",    # "Mummy, this is my new number, send money"
    "remote_access",           # install AnyDesk / screen share
    "other_scam",
    "not_scam",
]

VERDICTS = ["scam", "suspicious", "safe"]

# Step 1: read the screenshot. Pure perception, no judgement yet.
EXTRACT_SCHEMA = {
    "type": "object",
    "properties": {
        "message_text": {
            "type": "string",
            "description": "All readable text in the screenshot, in reading order, copied exactly.",
        },
        "sender": {"type": "string", "description": "Sender name, number or ID if visible, else empty."},
        "channel": {"type": "string", "enum": ["sms", "whatsapp", "email", "upi_app", "call_screen", "other"]},
        "has_qr_code": {"type": "boolean"},
        "language": {"type": "string", "enum": ["english", "hindi", "hinglish", "other"]},
    },
    "required": ["message_text", "sender", "channel", "has_qr_code", "language"],
}

# Step 2: judge. `reasoning` comes FIRST on purpose, so the model writes its short
# reasoning before it is forced to commit to a verdict.
CLASSIFY_SCHEMA = {
    "type": "object",
    "properties": {
        "reasoning": {"type": "string", "description": "2-3 short sentences. Facts only."},
        "verdict": {"type": "string", "enum": VERDICTS},
        "scam_type": {"type": "string", "enum": SCAM_TYPES},
        "confidence": {"type": "integer", "minimum": 0, "maximum": 100},
        "red_flags": {
            "type": "array",
            "items": {"type": "string"},
            "maxItems": 5,
            "description": "Short phrases quoting or describing the suspicious parts.",
        },
    },
    "required": ["reasoning", "verdict", "scam_type", "confidence", "red_flags"],
}
