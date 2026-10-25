"""All tunable settings in one place. Override any of them with environment variables."""

import os

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.getenv("KAVACH_MODEL", "gemma4:e4b")
DECISION_ENGINE = os.getenv("KAVACH_DECISION_ENGINE", "gemma").lower()  # "gemma" | "jev"

# Determinism: temperature 0 + fixed seed => same input gives the same output.
TEMPERATURE = float(os.getenv("KAVACH_TEMPERATURE", "0"))
SEED = int(os.getenv("KAVACH_SEED", "42"))

NUM_CTX = int(os.getenv("KAVACH_NUM_CTX", "4096"))
# Thinking mode costs tokens and time. Off by default (faster, better tok/s tie-breaker).
THINK = os.getenv("KAVACH_THINK", "false").lower() == "true"
TIMEOUT_S = int(os.getenv("KAVACH_TIMEOUT", "240"))

# Final-verdict thresholds on the fused 0-100 risk score.
SCAM_THRESHOLD = int(os.getenv("KAVACH_SCAM_THRESHOLD", "70"))
SUSPICIOUS_THRESHOLD = int(os.getenv("KAVACH_SUSPICIOUS_THRESHOLD", "40"))

# Fusion weights: how much we trust the model vs the deterministic rules.
MODEL_WEIGHT = float(os.getenv("KAVACH_MODEL_WEIGHT", "0.6"))
RULE_WEIGHT = 1.0 - MODEL_WEIGHT
