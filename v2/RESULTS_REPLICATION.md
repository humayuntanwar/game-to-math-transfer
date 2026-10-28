# V2 confirmatory replication

Fresh seeds [3, 4, 5, 6, 7, 8]; meanT = mean over math domains of (greedy cost − controller cost).

| mode | N | seed 3 | seed 4 | seed 5 | seed 6 | seed 7 | seed 8 | mean |
|---|---|---|---|---|---|---|---|---|
| fixed | 1 | -1.88 | -0.98 | -1.29 | -0.71 | -0.95 | -0.53 | -1.056 |
| fixed | 16 | -1.36 | -0.56 | -0.83 | -1.07 | -0.99 | -0.85 | -0.944 |
| online | 1 | -1.15 | -1.27 | -1.41 | -0.46 | -1.29 | -0.82 | -1.068 |
| online | 16 | -0.86 | -1.09 | -0.69 | -1.31 | -0.99 | -0.85 | -0.967 |
| random | 1 | -1.57 | -1.26 | -1.31 | -0.75 | -0.87 | -0.76 | -1.086 |
| random | 16 | -1.10 | -1.21 | -0.98 | -0.90 | -1.38 | -1.00 | -1.094 |

- R1 online(16) − fixed(16): per-seed [0.5, -0.53, 0.15, -0.24, -0.01, -0.0], mean -0.023, one-sided p = 0.625 → **FAILS**

- R2 interaction: per-seed [-0.23, -0.25, 0.27, -0.5, 0.34, 0.29], mean -0.011, one-sided p = 0.516 → **FAILS**

- R3 online(16) − random(16): per-seed [0.24, 0.11, 0.3, -0.41, 0.38, 0.15], mean +0.128, one-sided p = 0.172 → **FAILS**

**NOT REPLICATED** (requires R1 and R2).

