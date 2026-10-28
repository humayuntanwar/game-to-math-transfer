# V2 pre-registration

Written and committed **before** any V2 controller was evaluated on a math domain.
The only runs before this commit were difficulty probes of the procedural games
(greedy search only) and a smoke test that evaluated on the hand-made V1 games, never on math.

## Motivation from V1

In V1 a fixed 7-weight search controller trained on games transferred to 3-SAT
but hurt on Countdown and on the group word problem, and *adding* a plateau-heavy
game made things worse. The V1 oracle controllers (one trained per math problem)
want **opposite signs** on the same features. For example, `gain` is −1.51 for
Countdown and positive for the other two. A single fixed controller can only learn
a compromise.

## Hypothesis

Negative transfer from games is **interference between regime-specific search
skills**. A controller that identifies its regime *in-context*, from running
statistics of its own search (plateau rate, improvement rate, branching, step
size), can store several skills without them clashing. Therefore:

> Training on more diverse games helps a regime-conditioned controller and does not
> help (or hurts) a fixed controller, at equal compute.

## Design (fixed in `experiment_v2.py`)

- **Training games:** procedurally generated (`procgen.py`: XOR-mask games and
  lattice games with barriers, random knobs), filtered only for difficulty using
  greedy search. Nested: N ∈ {1, 2, 4, 8, 16} types from seed stream `s<seed>`.
- **Equal compute:** 24 training instances per run, regardless of N.
  CEM with population 24, 6 elite, 16 iterations, budget 3,000 expansions.
- **Modes:** `fixed` (V1 controller, 7 params), `online` (context-conditioned,
  35 params), `random` (same 35 params, but the context is random per instance
  and never measured: a capacity-matched control).
- **Seeds:** 0, 1, 2.
- **Evaluation:** zero-shot on the V1 math test sets (Countdown, group word,
  planted 3-SAT; 40 instances each) and the V1 hand-made games.

## Predictions (analysis code: `analyze_v2.py`)

T = greedy cost − controller cost; meanT = mean over the 3 math domains, averaged over seeds.

- **P1:** Spearman(N, meanT_online) > 0.
- **P2:** meanT_online(16) > meanT_fixed(16), and the online−fixed gap at N=16 is larger than at N=1.
- **P3:** meanT_online(16) > meanT_random(16).
- **P4 (stretch):** online controller at N=16 beats greedy on the group word problem (T > 0).

The headline hypothesis counts as **supported only if P1, P2 and P3 all hold**.
All results will be published whatever they show.

## Addendum (before any result was analyzed)

The first launch was killed by a container restart after 31 of 45 runs. While
checking whether resuming would be faithful, I found that lattice-game obstacles
were placed with Python's built-in `hash()` of a string, which is salted per
process. Runs after a restart would therefore have seen different game layouts
than runs before it. Fix: obstacles now use `zlib.crc32` (deterministic), and the
whole grid is rerun from scratch with `PYTHONHASHSEED=0`. The aborted partial
results are kept, **unanalyzed and unread**, in `results_v2_ABORTED_unanalyzed.json`.
Hypotheses, design, predictions and analysis code are unchanged.

## Confirmatory replication (registered after V2 results, before the replication ran)

The V2 grid met the pre-registered criteria (P1–P3 hold, P4 fails), but the
effects were about the size of the seed noise: an exploratory sign-flip test of
the P2 interaction gave p ≈ 0.09 with 3 seeds. The replication decides whether
the effect is real.

- **Fresh seeds 3–8.** Both the game types and the CEM noise are new. N ∈ {1, 16},
  all three modes, with code and compute identical to V2.
- **Tests:** one-sided exact sign-flip permutation tests over the 6 seeds
  (`analyze_replication.py`).
- **Criteria:** R1, online(16) > fixed(16); R2, the interaction; R3, online(16) >
  random-context(16). Each needs a positive mean and p < 0.05.
- **Verdict:** **replicated only if R1 and R2 hold.** Results will be published either way.
