"""Pre-registered analysis for V2 (written before any V2 math result existed).

T_d(run)  = greedy cost on math domain d (V1 results.json, same test instances)
            - run's cost on d.  Positive = better than greedy.
meanT(run) = mean of T_d over the 3 math domains.
Each (mode, N) cell = mean over seeds.

P1  Spearman(N, meanT_online) > 0 over N in {1,2,4,8,16}       diversity helps the conditioned controller
P2  meanT_online(16) > meanT_fixed(16) AND
    [online - fixed](16) > [online - fixed](1)                   conditioning x diversity interaction
P3  meanT_online(16) > meanT_random(16)                         conditioning, not extra parameters
P4  T_group_word online(16) > 0                                  stretch: fixes V1's worst failure
Headline hypothesis SUPPORTED iff P1, P2 and P3 all hold.
"""
import json
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
MATH = ["countdown", "group_word", "planted_3sat"]
HAND = ["sliding_tile", "lights_out", "maze"]


def spearman(x, y):
    rank = lambda v: {i: r for r, i in enumerate(sorted(range(len(v)), key=v.__getitem__))}
    rx, ry, n = rank(x), rank(y), len(x)
    return 1 - 6 * sum((rx[i] - ry[i]) ** 2 for i in range(n)) / (n * (n * n - 1))


def main():
    V1 = json.load(open(os.path.join(HERE, "..", "results.json")))["eval"]
    R = json.load(open(os.path.join(HERE, "results_v2.json")))
    greedy = {d: V1["greedy"][d]["mean_cost"] for d in MATH + HAND}
    Ns = R["config"]["Ns"]
    cell = {}
    for run in R["runs"].values():
        T = {d: greedy[d] - run["eval"][d]["cost"] for d in run["eval"]}
        cell.setdefault((run["mode"], run["N"]), []).append(T)
    avg = lambda mode, n, d: statistics.fmean(t[d] for t in cell[(mode, n)])
    meanT = lambda mode, n: statistics.fmean(avg(mode, n, d) for d in MATH)

    L = ["# V2 results\n", "T = greedy cost − controller cost on held-out test instances (positive = better than greedy). "
         "Each cell is the mean over seeds.\n", "## Mean transfer to math (3 domains)\n",
         "| N game types | fixed | online (conditioned) | random-context control |", "|---|---|---|---|"]
    for n in Ns:
        L.append(f"| {n} | " + " | ".join(f"{meanT(m, n):+.3f}" if (m, n) in cell else "–"
                                          for m in ("fixed", "online", "random")) + " |")
    for title, doms in (("Per math domain", MATH), ("Hand-made V1 games (also never seen)", HAND)):
        L += [f"\n## {title}\n", "| mode | N | " + " | ".join(doms) + " |", "|---|---|" + "---|" * len(doms)]
        for m in ("fixed", "online", "random"):
            for n in Ns:
                if (m, n) in cell:
                    L.append(f"| {m} | {n} | " + " | ".join(f"{avg(m, n, d):+.2f}" for d in doms) + " |")

    full = all((m, n) in cell for m in ("fixed", "online", "random") for n in Ns)
    if full:
        on = [meanT("online", n) for n in Ns]
        rho = spearman(Ns, on)
        p1 = rho > 0
        gap = lambda n: meanT("online", n) - meanT("fixed", n)
        p2 = meanT("online", 16) > meanT("fixed", 16) and gap(16) > gap(1)
        p3 = meanT("online", 16) > meanT("random", 16)
        p4 = avg("online", 16, "group_word") > 0
        v = lambda b: "**HOLDS**" if b else "**FAILS**"
        L += ["\n## Pre-registered predictions\n",
              f"- P1 Spearman(N, meanT_online) = {rho:+.2f} → {v(p1)}",
              f"- P2 online(16) − fixed(16) = {gap(16):+.3f}; gap(1) = {gap(1):+.3f} → {v(p2)}",
              f"- P3 online(16) = {meanT('online', 16):+.3f} vs random(16) = {meanT('random', 16):+.3f} → {v(p3)}",
              f"- P4 (stretch) group_word online(16) = {avg('online', 16, 'group_word'):+.3f} → {v(p4)}",
              f"\n**Headline hypothesis: {'SUPPORTED' if p1 and p2 and p3 else 'NOT SUPPORTED'}** (requires P1, P2, P3).\n"]
    out = "\n".join(L) + "\n"
    open(os.path.join(HERE, "RESULTS_V2.md"), "w").write(out)
    print(out)


if __name__ == "__main__":
    main()
