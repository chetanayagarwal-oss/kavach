"""The Kavach pipeline.

    screenshot ──► [1] Gemma reads it (OCR, JSON schema)
                         │
                         ▼
                   [2] regex rules (deterministic red flags + entities)
                         │
                         ▼
                   [3] Gemma judges (JSON schema, rule flags as hints)
                         │
                         ▼
                   [4] fuse model + rules → final verdict → fixed advice template

Everything runs against a local Ollama server. No cloud API is called.
"""

from __future__ import annotations

import base64
import json
import time
from pathlib import Path

import requests

from . import config
from .advice import build_advice
from .prompts import CLASSIFY_SYSTEM, EXTRACT_SYSTEM, FEW_SHOT, classify_user_message
from .rules import check_text
from .schema import CLASSIFY_SCHEMA, EXTRACT_SCHEMA, SCAM_TYPES, VERDICTS


class OllamaError(RuntimeError):
    pass


def _post_chat(payload: dict) -> dict:
    url = f"{config.OLLAMA_URL}/api/chat"
    r = requests.post(url, json=payload, timeout=config.TIMEOUT_S)
    if r.status_code == 400 and "think" in payload and "think" in r.text.lower():
        # Some model builds reject the `think` field. Retry without it.
        payload = {k: v for k, v in payload.items() if k != "think"}
        r = requests.post(url, json=payload, timeout=config.TIMEOUT_S)
    if r.status_code != 200:
        raise OllamaError(f"Ollama returned {r.status_code}: {r.text[:300]}")
    return r.json()


def call_model(messages: list[dict], schema: dict) -> tuple[dict, dict]:
    """One grammar-constrained call. Returns (parsed_json, stats)."""
    payload = {
        "model": config.MODEL,
        "messages": messages,
        "format": schema,          # JSON schema → constrained decoding
        "stream": False,
        "think": config.THINK,
        "options": {"temperature": config.TEMPERATURE, "seed": config.SEED, "num_ctx": config.NUM_CTX},
    }
    t0 = time.perf_counter()
    data = _post_chat(payload)
    wall = time.perf_counter() - t0

    content = data.get("message", {}).get("content", "")
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as e:  # should not happen with a schema, but never crash the demo
        raise OllamaError(f"Model output was not valid JSON: {content[:200]}") from e

    eval_count = data.get("eval_count", 0)
    eval_ns = data.get("eval_duration", 0) or 1
    stats = {
        "wall_s": round(wall, 3),
        "prompt_tokens": data.get("prompt_eval_count", 0),
        "output_tokens": eval_count,
        "decode_tok_s": round(eval_count / (eval_ns / 1e9), 2) if eval_count else 0.0,
    }
    return parsed, stats


def extract_from_image(image_path: str | Path) -> tuple[dict, dict]:
    img_b64 = base64.b64encode(Path(image_path).read_bytes()).decode()
    messages = [
        {"role": "system", "content": EXTRACT_SYSTEM},
        {"role": "user", "content": "Transcribe this screenshot.", "images": [img_b64]},
    ]
    return call_model(messages, EXTRACT_SCHEMA)


def classify(message_text: str, rule_lines: list[str]) -> tuple[dict, dict]:
    if config.DECISION_ENGINE == "jev":
        from .jev import classify_with_jev
        return classify_with_jev(message_text, rule_lines)

    messages = [{"role": "system", "content": CLASSIFY_SYSTEM}, *FEW_SHOT,
                {"role": "user", "content": classify_user_message(message_text, rule_lines)}]
    out, stats = call_model(messages, CLASSIFY_SCHEMA)
    # Belt and braces: enforce consistency the schema alone cannot express.
    if out.get("verdict") not in VERDICTS:
        out["verdict"] = "suspicious"
    if out.get("scam_type") not in SCAM_TYPES:
        out["scam_type"] = "other_scam"
    if out["verdict"] == "safe":
        out["scam_type"] = "not_scam"
    elif out["scam_type"] == "not_scam":
        out["scam_type"] = "other_scam"
    out["confidence"] = max(0, min(100, int(out.get("confidence", 50))))
    return out, stats


def model_risk(verdict: str, confidence: int) -> float:
    """Turn the model's (verdict, confidence) into a 0-100 risk number."""
    if verdict == "scam":
        return 50 + confidence / 2          # 50..100
    if verdict == "suspicious":
        return 35 + confidence * 0.3        # 35..65
    return (100 - confidence) * 0.35        # 0..35


def fuse(cls: dict, rule_score: int, has_critical: bool) -> tuple[int, str]:
    risk = config.MODEL_WEIGHT * model_risk(cls["verdict"], cls["confidence"]) + config.RULE_WEIGHT * rule_score
    if has_critical:                         # non-negotiable signals: OTP/PIN ask, digital arrest, AnyDesk, .apk
        risk = max(risk, config.SCAM_THRESHOLD + 5)
    if cls["verdict"] == "scam" and cls["confidence"] >= 85:
        risk = max(risk, config.SCAM_THRESHOLD)
    risk = int(round(min(100, risk)))
    if risk >= config.SCAM_THRESHOLD:
        return risk, "scam"
    if risk >= config.SUSPICIOUS_THRESHOLD:
        return risk, "suspicious"
    return risk, "safe"


def check(image_path: str | Path | None = None, text: str | None = None) -> dict:
    """Main entry point. Give a screenshot path, or raw message text, or both."""
    if not image_path and not text:
        raise ValueError("Give an image_path or text.")

    t0 = time.perf_counter()
    calls = []
    extracted = {"message_text": text or "", "sender": "", "channel": "other", "has_qr_code": False, "language": "other"}

    if image_path:
        ex, st = extract_from_image(image_path)
        calls.append({"step": "extract", **st})
        extracted.update(ex)
        if text:  # user also typed something: keep both
            extracted["message_text"] = f"{ex.get('message_text', '')}\n{text}".strip()

    rules = check_text(extracted["message_text"])
    cls, st = classify(extracted["message_text"], rules.lines_for_prompt())
    calls.append({"step": "classify", **st})

    risk, final = fuse(cls, rules.score, rules.has_critical)
    scam_type = cls["scam_type"] if final != "safe" else "not_scam"
    if final != "safe" and scam_type == "not_scam":
        scam_type = "other_scam"

    out_tokens = sum(c["output_tokens"] for c in calls)
    decode_time = sum(c["output_tokens"] / c["decode_tok_s"] for c in calls if c["decode_tok_s"])
    return {
        "verdict": final,
        "risk_score": risk,
        "scam_type": scam_type,
        "model": {"verdict": cls["verdict"], "confidence": cls["confidence"], "reasoning": cls["reasoning"],
                  "red_flags": cls["red_flags"]},
        "rules": rules.to_dict(),
        "extracted": extracted,
        "advice": build_advice(final, scam_type),
        "perf": {
            "model_name": config.MODEL,
            "total_s": round(time.perf_counter() - t0, 3),
            "output_tokens": out_tokens,
            "decode_tok_s": round(out_tokens / decode_time, 2) if decode_time else 0.0,
            "calls": calls,
        },
    }
