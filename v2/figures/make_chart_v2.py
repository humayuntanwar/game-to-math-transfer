"""Per-seed conditioning x diversity interaction: original V2 seeds vs replication.
Writes figures/replication.svg and .png (PNG needs Node + Playwright)."""
import json
import statistics
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
M = ["countdown", "group_word", "planted_3sat"]
V1 = json.load(open(ROOT.parent / "results.json"))["eval"]
g = {d: V1["greedy"][d]["mean_cost"] for d in M}


def load(f):
    R = json.load(open(ROOT / f))["runs"]
    return {(r["mode"], r["N"], r["seed"]): statistics.fmean(g[d] - r["eval"][d]["cost"] for d in M) for r in R.values()}


v = {**load("results_v2.json"), **load("replication_v2.json")}
I = lambda s: (v[("online", 16, s)] - v[("fixed", 16, s)]) - (v[("online", 1, s)] - v[("fixed", 1, s)])
groups = [("Original run (3 seeds)", [I(s) for s in range(3)], "#2a78d6"),
          ("Pre-registered replication (6 new seeds)", [I(s) for s in range(3, 9)], "#8a8984")]
W, H = 1600, 900
X0, X1, VMIN, VMAX = 620, 1500, -0.8, 1.4
sx = lambda x: X0 + (x - VMIN) / (VMAX - VMIN) * (X1 - X0)
o = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Inter, Helvetica, Arial, sans-serif">',
     f'<rect width="{W}" height="{H}" fill="#fcfcfb"/>',
     '<text x="80" y="92" font-size="40" font-weight="700" fill="#0b0b0b">My hypothesis passed its pre-registered test. Then it didn’t replicate.</text>',
     '<text x="80" y="140" font-size="24" fill="#52514e">Effect of in-context regime conditioning × game diversity on zero-shot transfer to math (per seed).</text>',
     '<text x="80" y="172" font-size="24" fill="#52514e">Dot = one training seed; bar = mean. Positive = the hypothesis’s predicted direction.</text>']
top, bot = 240, 700
for x in [-0.5, 0, 0.5, 1.0]:
    o.append(f'<line x1="{sx(x):.1f}" y1="{top}" x2="{sx(x):.1f}" y2="{bot}" stroke="{"#8a8984" if x == 0 else "#e6e5e1"}" stroke-width="{2 if x == 0 else 1}"/>')
    o.append(f'<text x="{sx(x):.1f}" y="{bot + 34}" font-size="20" fill="#52514e" text-anchor="middle">{"0" if x == 0 else f"{x:+g}"}</text>')
o.append(f'<text x="{sx(-0.4):.1f}" y="{bot + 72}" font-size="20" fill="#52514e" text-anchor="middle">◀ against hypothesis</text>')
o.append(f'<text x="{sx(0.7):.1f}" y="{bot + 72}" font-size="20" fill="#52514e" text-anchor="middle">supports hypothesis ▶</text>')
for gi, (label, xs, col) in enumerate(groups):
    y = 330 + gi * 220
    m = statistics.fmean(xs)
    o.append(f'<text x="80" y="{y + 8}" font-size="26" fill="#0b0b0b">{label}</text>')
    o.append(f'<text x="80" y="{y + 44}" font-size="22" fill="#52514e">mean {m:+.2f}' + (" · p ≈ 0.09 (exploratory)" if gi == 0 else " · p = 0.52") + '</text>')
    o.append(f'<line x1="{sx(m):.1f}" y1="{y - 40}" x2="{sx(m):.1f}" y2="{y + 40}" stroke="{col}" stroke-width="6" stroke-linecap="round"/>')
    for k, x in enumerate(xs):
        o.append(f'<circle cx="{sx(x):.1f}" cy="{y + (k % 3 - 1) * 14}" r="11" fill="{col}" stroke="#fcfcfb" stroke-width="2"/>')
o.append(f'<text x="80" y="{H - 22}" font-size="18" fill="#8a8984">Procedural games · 35-param context-conditioned vs 7-param fixed search controller · N = 1 vs 16 game types at equal compute</text>')
o.append("</svg>")
(HERE / "replication.svg").write_text("\n".join(o))
png = HERE / "replication.png"
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();const p=await b.newPage({{viewport:{{width:{W},height:{H}}}}});
await p.goto('file://{(HERE / "replication.svg").resolve()}');await p.screenshot({{path:'{png.resolve()}'}});await b.close();}})();"""
subprocess.run(["node", "-e", js], check=False)
print("wrote", png)
