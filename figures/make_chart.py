"""Builds figures/transfer.svg (+ .png via Playwright if available) from results.json.
Bar = mean over 3 games-trained controllers; dots = individual seeds.
Value = best classic search cost - controller cost (positive = controller better)."""
import json
import statistics
import subprocess
from pathlib import Path

HERE = Path(__file__).parent
E = json.load(open(HERE.parent / "results.json"))["eval"]
CLASSIC = ["greedy", "A*", "wA*(w=3)"]
ROWS = [("Games — trained on", [("15-puzzle", "sliding_tile"), ("Lights Out", "lights_out"), ("Maze", "maze")]),
        ("Math — never seen (zero-shot)", [("Planted 3-SAT", "planted_3sat"), ("Countdown arithmetic", "countdown"),
                                          ("Group word problem", "group_word")])]
POS, NEG = "#2a78d6", "#e34948"
W, H = 1600, 900
X0, X1, VMIN, VMAX = 560, 1480, -1.6, 1.6
sx = lambda v: X0 + (v - VMIN) / (VMAX - VMIN) * (X1 - X0)

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       'font-family="Inter, Helvetica, Arial, sans-serif">',
       f'<rect width="{W}" height="{H}" fill="#fcfcfb"/>',
       '<text x="80" y="92" font-size="40" font-weight="700" fill="#0b0b0b">Search skill learned in games helps on some math problems, hurts on others</text>',
       '<text x="80" y="140" font-size="24" fill="#52514e">Improvement over the best classic search (greedy / A* / weighted A*), in log search-expansions.</text>',
       '<text x="80" y="172" font-size="24" fill="#52514e">Bar = mean of 3 training seeds; dots = individual seeds.</text>']
y = 235
for v in (-1.5, -1, -0.5, 0, 0.5, 1, 1.5):
    x = sx(v)
    out.append(f'<line x1="{x:.1f}" y1="{y-20}" x2="{x:.1f}" y2="{y+490}" stroke="{"#8a8984" if v == 0 else "#e6e5e1"}" stroke-width="{2 if v == 0 else 1}"/>')
    out.append(f'<text x="{x:.1f}" y="{y+520}" font-size="20" fill="#52514e" text-anchor="middle">{"0" if v == 0 else f"{v:+g}"}</text>')
out.append(f'<text x="{sx(-0.8):.1f}" y="{y+556}" font-size="20" fill="#52514e" text-anchor="middle">◀ worse than classic search</text>')
out.append(f'<text x="{sx(0.8):.1f}" y="{y+556}" font-size="20" fill="#52514e" text-anchor="middle">better than classic search ▶</text>')
for group, items in ROWS:
    out.append(f'<text x="80" y="{y+8}" font-size="24" font-weight="700" fill="#0b0b0b">{group}</text>')
    y += 40
    for label, d in items:
        best = min(E[c][d]["mean_cost"] for c in CLASSIC)
        seeds = [best - E[f"games[{s}]"][d]["mean_cost"] for s in range(3)]
        m = statistics.fmean(seeds)
        x, z = sx(m), sx(0)
        col = POS if m >= 0 else NEG
        out.append(f'<text x="100" y="{y+33}" font-size="26" fill="#0b0b0b">{label}</text>')
        out.append(f'<rect x="{min(x, z):.1f}" y="{y+10}" width="{abs(x - z):.1f}" height="34" rx="4" fill="{col}"/>')
        for s in seeds:
            out.append(f'<circle cx="{sx(s):.1f}" cy="{y+27}" r="6" fill="#fcfcfb" stroke="#0b0b0b" stroke-width="2"/>')
        tx = (max(x, z) + 14) if m >= 0 else (min(x, z) - 14)
        tx = max(tx, max(sx(s) for s in seeds) + 16) if m >= 0 else min(tx, min(sx(s) for s in seeds) - 16)
        out.append(f'<text x="{tx:.1f}" y="{y+36}" font-size="24" font-weight="600" fill="#0b0b0b" '
                   f'text-anchor="{"start" if m >= 0 else "end"}">{m:+.2f}</text>')
        y += 62
    y += 30
out.append(f'<text x="80" y="{H-22}" font-size="18" fill="#8a8984">7-weight domain-agnostic search controller · trained with CEM on games only · 40 held-out instances per domain</text>')
out.append("</svg>")
(HERE / "transfer.svg").write_text("\n".join(out))

png = HERE / "transfer.png"
js = f"""const {{chromium}}=require('playwright');(async()=>{{const b=await chromium.launch();
const p=await b.newPage({{viewport:{{width:{W},height:{H}}}}});await p.goto('file://{HERE.resolve()}/transfer.svg');
await p.screenshot({{path:'{png.resolve()}'}});await b.close();}})();"""
subprocess.run(["node", "-e", js], check=False)
print("wrote", HERE / "transfer.svg", "and", png)
