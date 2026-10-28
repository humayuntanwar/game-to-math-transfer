# V2 results

T = greedy cost − controller cost on held-out test instances (positive = better than greedy). Each cell is the mean over seeds.

## Mean transfer to math (3 domains)

| N game types | fixed | online (conditioned) | random-context control |
|---|---|---|---|
| 1 | -0.864 | -0.988 | -1.133 |
| 2 | -1.097 | -1.073 | -1.021 |
| 4 | -0.916 | -1.367 | -0.918 |
| 8 | -0.870 | -1.027 | -1.005 |
| 16 | -1.175 | -0.788 | -1.015 |

## Per math domain

| mode | N | countdown | group_word | planted_3sat |
|---|---|---|---|---|
| fixed | 1 | +0.03 | -2.17 | -0.45 |
| fixed | 2 | -0.04 | -2.65 | -0.60 |
| fixed | 4 | +0.03 | -2.71 | -0.07 |
| fixed | 8 | +0.20 | -2.78 | -0.03 |
| fixed | 16 | +0.12 | -2.94 | -0.70 |
| online | 1 | -0.07 | -2.16 | -0.73 |
| online | 2 | -0.19 | -2.72 | -0.32 |
| online | 4 | -0.38 | -2.97 | -0.75 |
| online | 8 | +0.05 | -2.55 | -0.58 |
| online | 16 | -0.17 | -2.34 | +0.14 |
| random | 1 | -0.12 | -2.68 | -0.60 |
| random | 2 | +0.10 | -2.60 | -0.56 |
| random | 4 | +0.13 | -2.62 | -0.26 |
| random | 8 | +0.06 | -2.76 | -0.33 |
| random | 16 | +0.22 | -2.80 | -0.46 |

## Hand-made V1 games (also never seen)

| mode | N | sliding_tile | lights_out | maze |
|---|---|---|---|---|
| fixed | 1 | -0.88 | -0.62 | -0.16 |
| fixed | 2 | -1.06 | -0.99 | -0.18 |
| fixed | 4 | -1.19 | -0.45 | -0.20 |
| fixed | 8 | -1.42 | -0.66 | -0.25 |
| fixed | 16 | -1.46 | -0.16 | -0.19 |
| online | 1 | -0.64 | -1.35 | -0.24 |
| online | 2 | -1.33 | -0.85 | -0.37 |
| online | 4 | -1.47 | -0.38 | -0.43 |
| online | 8 | -1.45 | -0.49 | -0.20 |
| online | 16 | -0.84 | -0.75 | -0.23 |
| random | 1 | -1.24 | -0.63 | -0.20 |
| random | 2 | -1.33 | -0.54 | -0.22 |
| random | 4 | -1.13 | -0.45 | -0.20 |
| random | 8 | -1.09 | -0.77 | -0.17 |
| random | 16 | -1.30 | -0.61 | -0.21 |

## Pre-registered predictions

- P1 Spearman(N, meanT_online) = +0.30 → **HOLDS**
- P2 online(16) − fixed(16) = +0.387; gap(1) = -0.123 → **HOLDS**
- P3 online(16) = -0.788 vs random(16) = -1.015 → **HOLDS**
- P4 (stretch) group_word online(16) = -2.339 → **FAILS**

**Headline hypothesis: SUPPORTED** (requires P1, P2, P3).

