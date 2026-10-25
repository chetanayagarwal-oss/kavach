"""Reliability eval: every sample x N runs (default 3).

This produces exactly what the "Best Local Agentic Tool" judges score:
task success rate, reliability (same answer across runs), and tokens/sec.

Run:  python eval/eval.py                 # images through the full pipeline
      python eval/eval.py --text-only     # skip OCR, use labels.csv text (faster)
      python eval/eval.py --runs 3 --limit 10
"""

from __future__ import annotations

import argparse
import csv
import json
import platform
import shutil
import statistics
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from kavach import config  # noqa: E402
from kavach.pipeline import check  # noqa: E402

DATA = ROOT / "data"
RESULTS = ROOT / "results"


def hardware() -> str:
    parts = [f"{platform.system()} {platform.release()}", platform.machine(), platform.processor() or ""]
    try:
        import psutil  # optional
        parts.append(f"{round(psutil.virtual_memory().total / 2**30)} GB RAM")
    except ImportError:
        pass
    if shutil.which("nvidia-smi"):
        try:
            gpu = subprocess.run(["nvidia-smi", "--query-gpu=name,memory.total", "--format=csv,noheader"],
                                 capture_output=True, text=True, timeout=10).stdout.strip()
            parts.append(f"GPU: {gpu}")
        except Exception:
            pass
    return " | ".join(p for p in parts if p)


def flagged(v: str) -> bool:
    return v in ("scam", "suspicious")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--text-only", action="store_true")
    a = ap.parse_args()

    rows = list(csv.DictReader((DATA / "labels.csv").open(encoding="utf-8")))
    if a.limit:
        rows = rows[: a.limit]
    RESULTS.mkdir(exist_ok=True)

    records = []
    for run in range(1, a.runs + 1):
        for row in rows:
            t0 = time.perf_counter()
            try:
                if a.text_only:
                    res = check(text=row["text"])
                else:
                    res = check(image_path=DATA / row["file"])
                err = ""
            except Exception as e:  # keep going, count it as a failure
                res, err = None, str(e)[:200]
            rec = {
                "run": run, "file": row["file"], "label": row["label"], "true_type": row["scam_type"],
                "verdict": res["verdict"] if res else "error",
                "pred_type": res["scam_type"] if res else "error",
                "risk": res["risk_score"] if res else -1,
                "tok_s": res["perf"]["decode_tok_s"] if res else 0,
                "latency_s": round(time.perf_counter() - t0, 2),
                "error": err,
            }
            rec["correct"] = (flagged(rec["verdict"]) == (rec["label"] == "scam")) and not err
            records.append(rec)
            print(f"run {run} {row['file']:<20} true={row['label']:<5} pred={rec['verdict']:<10} "
                  f"risk={rec['risk']:<4} {rec['tok_s']} tok/s {'OK' if rec['correct'] else 'XX'}", flush=True)

    with (RESULTS / "eval_runs.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)

    # ---------- metrics ----------
    per_run = []
    for run in range(1, a.runs + 1):
        rr = [r for r in records if r["run"] == run]
        tp = sum(1 for r in rr if r["label"] == "scam" and flagged(r["verdict"]))
        fn = sum(1 for r in rr if r["label"] == "scam" and not flagged(r["verdict"]))
        fp = sum(1 for r in rr if r["label"] == "safe" and flagged(r["verdict"]))
        tn = sum(1 for r in rr if r["label"] == "safe" and not flagged(r["verdict"]))
        type_ok = sum(1 for r in rr if r["label"] == "scam" and r["pred_type"] == r["true_type"])
        n_scam = tp + fn
        per_run.append({
            "run": run, "accuracy": (tp + tn) / len(rr), "scam_recall": tp / n_scam if n_scam else 0,
            "false_positive_rate": fp / (fp + tn) if (fp + tn) else 0, "type_accuracy": type_ok / n_scam if n_scam else 0,
            "tp": tp, "fn": fn, "fp": fp, "tn": tn,
        })

    by_file: dict[str, list[str]] = {}
    for r in records:
        by_file.setdefault(r["file"], []).append(r["verdict"])
    consistent = sum(1 for v in by_file.values() if len(set(v)) == 1)
    consistency = consistent / len(by_file)
    toks = [r["tok_s"] for r in records if r["tok_s"]]
    lats = [r["latency_s"] for r in records if not r["error"]]
    errors = Counter(r["error"] for r in records if r["error"])

    summary = {
        "model": config.MODEL, "hardware": hardware(), "samples": len(rows), "runs": a.runs,
        "mode": "text-only" if a.text_only else "image (OCR + classify)",
        "per_run": per_run, "consistency_all_runs_same_verdict": consistency,
        "median_decode_tok_s": statistics.median(toks) if toks else 0,
        "median_latency_s": statistics.median(lats) if lats else 0, "errors": dict(errors),
    }
    (RESULTS / "eval_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    md = [
        "# Kavach eval report", "",
        f"- **Model:** `{config.MODEL}` (temperature {config.TEMPERATURE}, seed {config.SEED}, thinking {'on' if config.THINK else 'off'})",
        f"- **Hardware:** {summary['hardware']}",
        f"- **Mode:** {summary['mode']}",
        f"- **Samples:** {len(rows)} x {a.runs} runs", "",
        "| Run | Accuracy | Scam recall | False-positive rate | Scam-type accuracy | TP | FN | FP | TN |",
        "|---|---|---|---|---|---|---|---|---|",
    ]
    for p in per_run:
        md.append(f"| {p['run']} | {p['accuracy']:.1%} | {p['scam_recall']:.1%} | {p['false_positive_rate']:.1%} | "
                  f"{p['type_accuracy']:.1%} | {p['tp']} | {p['fn']} | {p['fp']} | {p['tn']} |")
    md += [
        "",
        f"- **Consistency (same verdict in all {a.runs} runs):** {consistency:.1%} ({consistent}/{len(by_file)} samples)",
        f"- **Median decode speed:** {summary['median_decode_tok_s']:.1f} tokens/sec",
        f"- **Median end-to-end latency:** {summary['median_latency_s']:.1f} s per screenshot",
        f"- **Errors:** {sum(errors.values())}",
        "", "Raw per-run results: `results/eval_runs.csv`",
    ]
    (RESULTS / "EVAL_REPORT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print("\n".join(md))


if __name__ == "__main__":
    main()
