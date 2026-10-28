"""V2 controller: the V1 features, with weights modulated by an in-context
reading of the landscape, so one controller can behave differently in
different regimes.

    w_eff = W0 + W1 @ (c - C_MID)          (7 + 7*4 = 35 parameters)

c = running statistics of the search so far (causal, smoothed with a prior):
  0 p_flat    fraction of generated children with h == h(parent)
  1 p_better  fraction with h <  h(parent)
  2 branch    log(mean branching) / 5
  3 step      mean |dh| / h(start)

mode "online": c is measured from the current search (the real thing)
mode "random": c is drawn once per instance at random, never measured
               (capacity-matched control: same 35 parameters, uninformative context)
mode "fixed":  plain V1 controller (W1 = 0, 7 parameters)
"""
import heapq
import math
import random
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

NF, NC = 7, 4
C_MID = (0.3, 0.3, 0.4, 0.1)
C_RANGE = ((0.0, 0.7), (0.0, 0.5), (0.1, 0.9), (0.0, 0.3))


def unpack(theta):
    W0 = list(theta[:NF])
    W1 = [list(theta[NF + j * NF: NF + (j + 1) * NF]) for j in range(NC)] if len(theta) > NF else None
    return W0, W1


def ctx_search(inst, theta, budget, mode="online", rand_seed=0):
    W0, W1 = unpack(theta)
    s0 = inst.start
    h0 = inst.h(s0)
    if h0 == 0:
        return 0
    inv_h0 = 1.0 / h0
    log_b = math.log1p(budget)
    if mode == "random":
        rr = random.Random(rand_seed)
        cr = [rr.uniform(lo, hi) for lo, hi in C_RANGE]
    bins = {}
    open_ = [(0.0, 0, s0, 0, h0)]
    seen = {s0}
    best_h, best_g, last_improve = h0, 0, 0
    tick = exp = 0
    n_flat = n_better = n_tot = 0
    sum_dh = sum_br = 0.0
    w = W0
    while open_ and exp < budget:
        _, _, s, g, hp = heapq.heappop(open_)
        exp += 1
        allk = inst.expand(s)
        for _, hc in allk:
            n_tot += 1
            n_flat += hc == hp
            n_better += hc < hp
            sum_dh += abs(hc - hp) * inv_h0
        sum_br += len(allk)
        if W1 is not None:
            if mode == "online":
                c = ((n_flat + 1) / (n_tot + 3), (n_better + 1) / (n_tot + 3),
                     math.log(max(1.0, sum_br / exp)) / 5, min(1.0, (sum_dh + 0.1) / (n_tot + 1)))
            else:
                c = cr
            w = [W0[k] + sum(W1[j][k] * (c[j] - C_MID[j]) for j in range(NC)) for k in range(NF)]
        kids = [(c_, hc) for c_, hc in allk if c_ not in seen]
        if not kids:
            continue
        order = sorted(range(len(kids)), key=lambda i: kids[i][1])
        denom = max(1, len(kids) - 1)
        g1 = g + 1
        stall = (exp - last_improve) / budget
        w0, w1, w2, w3, w4, w5, w6 = w
        for rank, i in enumerate(order):
            c_, hc = kids[i]
            if hc == 0:
                return exp
            seen.add(c_)
            hr = hc * inv_h0
            b = int(hr * 40)
            cnt = bins.get(b, 0) + 1
            bins[b] = cnt
            if hc < best_h:
                best_h, best_g, last_improve = hc, g1, exp
            dr = g1 / (1 + best_g)
            p = (w0 * hr + w1 * (hp - hc) * inv_h0 + w2 * dr
                 + w3 * math.log1p(cnt) / log_b + w4 * rank / denom
                 + w5 * stall + w6 * stall * dr)
            tick += 1
            heapq.heappush(open_, (p, tick, c_, g1, hc))
    return None
