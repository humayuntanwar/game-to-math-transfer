"""Procedurally generated synthetic games (no human design).

A *game type* is sampled from one of two families with random knobs; instances
of a type share its rules and differ in start state. Knobs deliberately span
the landscape regimes V1 lacked (plateaus, deception, wide/narrow branching).

  mask    : state = n-bit string, moves = k random XOR masks, goal = all zeros.
            h = ceil(weighted popcount / q). q > 1 creates plateaus;
            dense masks create deception (a needed move can raise h a lot).
  lattice : state = point in a d-dim box, moves = k random integer vectors
            (+ inverses), hashed obstacles, goal = origin.
            h = ceil(weighted L1 / q).

Same interface as ../domains.py: .start, .h(s), .expand(s) -> [(child, h)].
"""
import random
import zlib


class GameType:
    def __init__(self, seed):
        self.seed = seed
        r = random.Random(f"type:{seed}")
        self.family = r.choice(["mask", "lattice"])
        if self.family == "mask":
            self.n = r.randint(20, 36)
            self.k = r.randint(10, 36)
            dens = r.uniform(0.06, 0.35)
            self.masks = []
            while len(self.masks) < self.k:
                m = sum(1 << b for b in range(self.n) if r.random() < dens)
                if m and m not in self.masks:
                    self.masks.append(m)
            wmax = r.choice([1, 1, 2, 4])
            w = [r.randint(1, wmax) for _ in range(self.n)]
            self.tables = [[sum(w[8 * c + b] for b in range(8) if (v >> b) & 1 and 8 * c + b < self.n)
                            for v in range(256)] for c in range((self.n + 7) // 8)]
            self.q = r.choice([1, 1, 2, 3, 5])
            self.scramble = (r.randint(7, 11), r.randint(12, 20))
            self.knobs = dict(n=self.n, k=self.k, dens=round(dens, 2), wmax=wmax, q=self.q)
        else:
            self.d = r.randint(2, 4)
            self.R = r.randint(*{2: (14, 30), 3: (8, 13), 4: (5, 7)}[self.d])
            m = r.randint(1, 4)
            half = []
            while len(half) < r.randint(3, 7) or not half:
                v = tuple(r.randint(-m, m) for _ in range(self.d))
                if any(v) and v not in half:
                    half.append(v)
            self.moves = half + [tuple(-x for x in v) for v in half]
            self.rho = r.choice([0.0, 0.1, 0.2, 0.3, 0.4])
            self.w = [r.randint(1, 3) for _ in range(self.d)]
            self.q = r.choice([1, 1, 2, 4, 6])
            # deceptive barriers: slabs c <= |x[a]| <= c+m (thick enough that no move jumps them) with one small gap placed far from the origin's line of sight
            self.barriers = []
            for _ in range(r.randint(1, 3)):
                a = r.randrange(self.d)
                c = r.choice([-1, 1]) * r.randint(2, max(2, self.R // 2))
                gap = tuple(r.choice([-1, 1]) * r.randint(self.R // 2, self.R) for _ in range(self.d))
                self.barriers.append((a, c, c + (m if c > 0 else -m), gap, r.randint(1, 2)))
            self.knobs = dict(d=self.d, R=self.R, m=m, moves=len(self.moves), rho=self.rho, q=self.q,
                              barriers=len(self.barriers))

    _bfs = None

    def far_states(self):
        """BFS from the goal over the whole box (cached per type); return the
        reachable states in the farthest 30% by true distance."""
        if self._bfs is None:
            from collections import deque
            probe = LatticeGame.__new__(LatticeGame)
            probe.T = self
            o = (0,) * self.d
            dist, q = {o: 0}, deque([o])
            while q:
                p = q.popleft()
                for c, _ in probe._kids(p):
                    if c not in dist:
                        dist[c] = dist[p] + 1
                        q.append(c)
            cut = sorted(dist.values())[int(0.7 * (len(dist) - 1))]
            self._bfs = sorted(p for p, v in dist.items() if v >= max(cut, 1))
        return self._bfs

    def instance(self, i):
        return (MaskGame if self.family == "mask" else LatticeGame)(self, random.Random(f"inst:{self.seed}:{i}"))

    def __repr__(self):
        return f"{self.family}{self.knobs}"


class MaskGame:
    def __init__(self, T, r):
        self.T = T
        while True:
            s = 0
            for m in r.sample(T.masks, min(len(T.masks), r.randint(*T.scramble))):
                s ^= m
            if s:
                break
        self.start = s

    def h(self, s):
        tot = 0
        for t in self.T.tables:
            tot += t[s & 255]
            s >>= 8
        return -(-tot // self.T.q)

    def expand(self, s):
        return [(s ^ m, self.h(s ^ m)) for m in self.T.masks]


class LatticeGame:
    def __init__(self, T, r):
        self.T = T
        far = T.far_states()
        self.start = r.choice(far) if far else (1,) + (0,) * (T.d - 1)

    def blocked(self, p):
        if not any(p):
            return False
        for a, c0, c1, gap, gw in self.T.barriers:
            if min(c0, c1) <= p[a] <= max(c0, c1) and max(abs(x - g) for j, (x, g) in enumerate(zip(p, gap)) if j != a) > gw:
                return True
        # deterministic across processes (built-in hash() of str is salted per process)
        return zlib.crc32(f"{self.T.seed}|{p}".encode()) % 1000 < self.T.rho * 1000

    def h(self, p):
        return -(-sum(w * abs(x) for w, x in zip(self.T.w, p)) // self.T.q)

    def _kids(self, p):
        R = self.T.R
        out = []
        for v in self.T.moves:
            c = tuple(a + b for a, b in zip(p, v))
            if all(-R <= x <= R for x in c) and not self.blocked(c):
                out.append((c, None))
        return out

    def expand(self, p):
        return [(c, self.h(c)) for c, _ in self._kids(p)]


def accepted_types(stream, count, budget, probe=8):
    """Draw game types from a seed stream; keep those of useful difficulty
    (greedy solves >= 2 of 8 probes, median >= 60 expansions). Nested: first N of the list."""
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from search import classic_search
    out, i = [], 0
    while len(out) < count:
        T = GameType(f"{stream}:{i}")
        i += 1
        res = [classic_search(T.instance(f"probe{j}"), budget, "greedy") for j in range(probe)]
        ok = sorted(x for x in res if x is not None)
        if len(ok) >= 2 and ok[len(ok) // 2] >= 60:
            out.append(T)
    return out
