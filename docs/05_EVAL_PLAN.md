# 05 · Evaluation plan

The Local Agentic track scores **task success rate, reliability, practical usefulness**, with **tokens/sec** as tie-breaker,
and asks for **3 repeated runs**. `eval/eval.py` measures all of that in one command.

## Dataset

| Source | Count | How |
|---|---|---|
| Synthetic screenshots | 30 (18 scam, 12 safe) | `python data/make_samples.py` — fictional numbers/UPI IDs/links |
| Team's own real messages (optional, adds credibility) | 5–10 | Screenshot real spam you received; **blur names and numbers**; add rows to `labels.csv` |

`data/labels.csv` columns: `file, label (scam|safe), scam_type, text`.
The `text` column lets you run a fast text-only eval without OCR.

Safe samples are deliberately tricky: a real OTP message ("do not share"), a money-credited alert, an electricity bill
from the official board, a train PNR message. These test **false positives**, which matter as much as catching scams —
a checker that screams "SCAM" at everything is useless.

## Metrics

| Metric | Meaning | Target |
|---|---|---|
| Accuracy | flagged (scam/suspicious) vs safe, matches label | ≥ 90% |
| Scam recall | % of scams caught | ≥ 95% |
| False-positive rate | % of safe messages wrongly flagged | ≤ 10% |
| Scam-type accuracy | correct type among scams | ≥ 60% (nice-to-have) |
| **Consistency** | % of samples with the **same verdict in all 3 runs** | **100%** (temp 0 + seed) |
| Decode tok/s | output tokens ÷ decode time (from Ollama) | report honestly |
| Latency | seconds per screenshot end-to-end | < 15 s on laptop GPU |

## Commands

```bash
python eval/eval.py --text-only --runs 1     # 1-2 min, while tuning
python eval/eval.py                          # final: images, 30 x 3 runs
python eval/eval.py --limit 10               # quick image smoke test
KAVACH_MODEL=gemma4:e2b python eval/eval.py  # compare the smaller model
```

Outputs:
- `results/EVAL_REPORT.md` → paste into README "Results"
- `results/eval_runs.csv` → every single prediction (proof for judges)
- `results/eval_summary.json` → machine-readable

## How to present it

Put this table on one slide and in the README:

```
Gemma 4 E4B · <your laptop> · 30 screenshots × 3 runs
Accuracy 9x% · Scam recall 9x% · False positives x/12 · Consistency 100% · xx tok/s
```

And one honest line: *"Test set is small and partly synthetic; next step is a real crowdsourced set."*
Judges trust teams that state limits.

## Time budget

On a laptop GPU, expect roughly 5–15 s per screenshot (two model calls). 30 × 3 = 90 checks ≈ 10–20 min.
**Start the full eval by hour 3:45 at the latest**, and work on the README/pitch while it runs.
On CPU only, use `--text-only` for the 3-run table and show a few image runs live.
