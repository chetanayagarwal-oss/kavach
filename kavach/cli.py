"""Command line: python -m kavach.cli --image shot.png   (or --text "message")

Prints JSON, so other agents (Hermes, Claude Code, Codex...) can call it as a tool.
"""

import argparse
import json
import sys

from .pipeline import OllamaError, check


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Kavach: offline scam-message checker")
    p.add_argument("--image", help="path to a screenshot (png/jpg)")
    p.add_argument("--text", help="message text, if you don't have a screenshot")
    p.add_argument("--brief", action="store_true", help="print only verdict, type, risk, advice")
    a = p.parse_args()
    if not a.image and not a.text:
        p.error("give --image or --text")
    try:
        res = check(image_path=a.image, text=a.text)
    except OllamaError as e:
        print(json.dumps({"error": str(e), "hint": "Is Ollama running? Try: ollama serve"}), file=sys.stderr)
        return 2
    if a.brief:
        res = {k: res[k] for k in ("verdict", "scam_type", "risk_score", "advice")}
    print(json.dumps(res, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
