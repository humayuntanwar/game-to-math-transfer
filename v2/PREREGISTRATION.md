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
