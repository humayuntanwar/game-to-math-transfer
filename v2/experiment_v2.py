"""V2: does in-context regime conditioning turn game diversity into transfer?

Grid: mode in {fixed, online, random} x N game types in {1,2,4,8,16} x seed in {0,1,2}.
Every run gets the SAME compute: 24 training instances spread over N procedurally
generated game types (from seed stream s<seed>), CEM with POP x ITERS evaluations.
Each trained controller is then evaluated zero-shot on the V1 math test sets
(and the V1 hand-made games). Results are appended to results_v2.json after
every run, so the grid can resume.

    python3 experiment_v2.py           # full grid (~3.5h on 4 cores)
    SMOKE=1 python3 experiment_v2.py   # tiny config, hand-games eval only
"""
import json
import os
import random
import statistics
import sys
import time
from multiprocessing import Pool

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, HERE)

from domains import GAMES, MATH, make_instances  # noqa: E402
from procgen import accepted_types               # noqa: E402
from search import GREEDY, cost                  # noqa: E402
from search_v2 import NF, NC, ctx_search         # noqa: E402

SMOKE = bool(os.environ.get("SMOKE"))
BUDGET = 3000
N_TRAIN = 8 if SMOKE else 24
POP, ELITE, ITERS = (8, 2, 2) if SMOKE else (24, 6, 16)
NS = [1, 4] if SMOKE else [1, 2, 4, 8, 16]
SEEDS = [0] if SMOKE else [0, 1, 2]
# replication override, e.g. NS=1,16 SEEDS=3,4,5,6,7,8 OUT=replication_v2.json
if os.environ.get("NS"):
    NS = [int(x) for x in os.environ["NS"].split(",")]
if os.environ.get("SEEDS"):
    SEEDS = [int(x) for x in os.environ["SEEDS"].split(",")]
MODES = ["fixed", "online", "random"]
TARGETS = list(GAMES) if SMOKE else list(MATH) + list(GAMES)
OUT = os.path.join(HERE, os.environ.get("OUT", "smoke_v2.json" if SMOKE else "results_v2.json"))

_cache = {}


def train_set(n, seed):
    key = ("train", n, seed)
    if key not in _cache:
        types = _cache.setdefault(("types", seed), accepted_types(f"s{seed}", max(NS), BUDGET))[:n]
        _cache[key] = [types[i % n].instance(f"train{i // n}") for i in range(N_TRAIN)]
    return _cache[key]


def test_set(d):
    key = ("test", d)
    if key not in _cache:
        _cache[key] = make_instances(d, 40, "test")
    return _cache[key]


def fitness(args):
    theta, mode, n, seed = args
    return statistics.fmean(cost(ctx_search(inst, theta, BUDGET, mode, rand_seed=i), BUDGET)
                            for i, inst in enumerate(train_set(n, seed)))


def cem(pool, mode, n, seed):
    dim = NF if mode == "fixed" else NF + NF * NC
    rng = random.Random(f"cem:{mode}:{n}:{seed}")
    mu = list(GREEDY) + [0.0] * (dim - NF)
    sigma = [1.0] * NF + [2.0] * (dim - NF)
    best = (fitness((tuple(mu), mode, n, seed)), tuple(mu))
    for _ in range(ITERS):
        cands = [tuple(m + s * rng.gauss(0, 1) for m, s in zip(mu, sigma)) for _ in range(POP)]
        fits = pool.map(fitness, [(c, mode, n, seed) for c in cands])
        ranked = sorted(zip(fits, cands))
        if ranked[0][0] < best[0]:
            best = ranked[0]
        elite = [c for _, c in ranked[:ELITE]]
        mu = [statistics.fmean(e[k] for e in elite) for k in range(dim)]
        sigma = [max(0.05, statistics.pstdev(e[k] for e in elite)) for k in range(dim)]
    return best


def evaluate(args):
    theta, mode, d = args
    # random-context control draws its context from a seed disjoint from training
    res = [ctx_search(inst, theta, BUDGET, mode, rand_seed=10_000 + i) for i, inst in enumerate(test_set(d))]
    return d, statistics.fmean(cost(r, BUDGET) for r in res), sum(r is not None for r in res) / len(res)


def main():
    t0 = time.time()
    done = json.load(open(OUT)) if os.path.exists(OUT) else {"config": dict(
        budget=BUDGET, n_train=N_TRAIN, pop=POP, elite=ELITE, iters=ITERS, Ns=NS, seeds=SEEDS), "runs": {}}
    with Pool(4) as pool:
        for n in NS:
            for seed in SEEDS:
                for mode in MODES:
                    key = f"{mode}|N={n}|seed={seed}"
                    if key in done["runs"]:
                        continue
                    fit, theta = cem(pool, mode, n, seed)
                    ev = pool.map(evaluate, [(theta, mode, d) for d in TARGETS])
                    done["runs"][key] = {"mode": mode, "N": n, "seed": seed, "train_fit": fit, "theta": theta,
                                         "types": [repr(t) for t in train_set_types(n, seed)],
                                         "eval": {d: {"cost": c, "solve": s} for d, c, s in ev}}
                    json.dump(done, open(OUT, "w"), indent=1)
                    print(f"[{time.time() - t0:7.0f}s] {key:24s} train {fit:.3f}", flush=True)


def train_set_types(n, seed):
    train_set(n, seed)
    return _cache[("types", seed)][:n]


if __name__ == "__main__":
    main()
