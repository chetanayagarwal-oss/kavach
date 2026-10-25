# Kavach eval report

- **Model:** `gemma4:e4b` (temperature 0.0, seed 42, thinking off)
- **Hardware:** Windows 11 | AMD64 | Intel64 Family 6 Model 186 Stepping 2, GenuineIntel | 16 GB RAM | GPU: NVIDIA GeForce RTX 4050 Laptop GPU, 6141 MiB
- **Mode:** image (OCR + classify)
- **Samples:** 30 x 3 runs

| Run | Accuracy | Scam recall | False-positive rate | Scam-type accuracy | TP | FN | FP | TN |
|---|---|---|---|---|---|---|---|---|
| 1 | 100.0% | 100.0% | 0.0% | 66.7% | 18 | 0 | 0 | 12 |
| 2 | 100.0% | 100.0% | 0.0% | 66.7% | 18 | 0 | 0 | 12 |
| 3 | 100.0% | 100.0% | 0.0% | 66.7% | 18 | 0 | 0 | 12 |

- **Consistency (same verdict in all 3 runs):** 100.0% (30/30 samples)
- **Median decode speed:** 54.2 tokens/sec
- **Median end-to-end latency:** 3.6 s per screenshot
- **Errors:** 0

Raw per-run results: `results/eval_runs.csv`
