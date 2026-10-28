"""Pre-registered confirmatory replication of V2 (written before the replication ran).

Fresh seeds 3..8 (game types AND CEM noise both new), N in {1, 16}, all three modes.
Per seed s:  D16(s) = meanT_online(16,s) - meanT_fixed(16,s)
             I(s)   = D16(s) - [meanT_online(1,s) - meanT_fixed(1,s)]
             P(s)   = meanT_online(16,s) - meanT_random(16,s)
One-sided exact sign-flip permutation test over the 6 seeds (64 sign patterns).

R1  mean D16 > 0, p < 0.05     conditioned beats fixed at high diversity
R2  mean I   > 0, p < 0.05     conditioning x diversity interaction
R3  mean P   > 0, p < 0.05     conditioning, not extra parameters
REPLICATED iff R1 and R2 hold.
"""
import itertools
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
MATH = ["countdown", "group_word", "planted_3sat"]


def signflip_p(xs):
    obs = statistics.fmean(xs)
    pats = list(itertools.product([1, -1], repeat=len(xs)))
    return sum(statistics.fmean(s * x for s, x in zip(p, xs)) >= obs - 1e-12 for p in pats) / len(pats)


def main():
    V1 = json.load(open(os.path.join(HERE, "..", "results.json")))["eval"]
    R = json.load(open(os.path.join(HERE, "replication_v2.json")))["runs"]
    g = {d: V1["greedy"][d]["mean_cost"] for d in MATH}
    v = {(r["mode"], r["N"], r["seed"]): statistics.fmean(g[d] - r["eval"][d]["cost"] for d in MATH) for r in R.values()}
    seeds = sorted({k[2] for k in v})
    D16 = [v[("online", 16, s)] - v[("fixed", 16, s)] for s in seeds]
    I = [D16[i] - (v[("online", 1, s)] - v[("fixed", 1, s)]) for i, s in enumerate(seeds)]
    P = [v[("online", 16, s)] - v[("random", 16, s)] for s in seeds]
    L = ["# V2 confirmatory replication\n", f"Fresh seeds {seeds}; meanT = mean over math domains of (greedy cost − controller cost).\n",
         "| mode | N | " + " | ".join(f"seed {s}" for s in seeds) + " | mean |", "|---|---|" + "---|" * (len(seeds) + 1)]
    for m in ("fixed", "online", "random"):
        for n in (1, 16):
            xs = [v[(m, n, s)] for s in seeds]
            L.append(f"| {m} | {n} | " + " | ".join(f"{x:+.2f}" for x in xs) + f" | {statistics.fmean(xs):+.3f} |")
    res = []
    for name, xs, desc in (("R1", D16, "online(16) − fixed(16)"), ("R2", I, "interaction"), ("R3", P, "online(16) − random(16)")):
        m, p = statistics.fmean(xs), signflip_p(xs)
        ok = m > 0 and p < 0.05
        res.append(ok)
        L.append(f"\n- {name} {desc}: per-seed {[round(x, 2) for x in xs]}, mean {m:+.3f}, one-sided p = {p:.3f} → **{'HOLDS' if ok else 'FAILS'}**")
    L.append(f"\n**{'REPLICATED' if res[0] and res[1] else 'NOT REPLICATED'}** (requires R1 and R2).\n")
    out = "\n".join(L) + "\n"
    open(os.path.join(HERE, "RESULTS_REPLICATION.md"), "w").write(out)
    print(out)


if __name__ == "__main__":
    main()
