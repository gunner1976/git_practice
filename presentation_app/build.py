"""Inline the app's modules into index.html (one module script; three.js resolved through the import map)."""
import re
from pathlib import Path
D = Path(__file__).parent; S = D / "src"
order = ["engine.js", "charts.js", "field3d.js", "slides_core.js", "slides_wells.js", "slides.js", "main.js"]
three = set(); body = []
for f in order:
    t = (S / f).read_text()
    for m in re.findall(r"^import .* from '(?:three|three/addons/[^']+)';\s*$", t, flags=re.M): three.add(m.strip())
    t = re.sub(r"^import .* from '(?:three|three/addons/[^']+|\./[^']+)';\s*$", "", t, flags=re.M)
    t = re.sub(r"^const d3 = window\.d3;\s*$", "", t, flags=re.M)
    t = re.sub(r"^export (?=(const|function|class|async function|let) )", "", t, flags=re.M)
    body.append(f"// ===== {f}\n{t}")
js = "\n".join(sorted(three)) + "\nconst d3 = window.d3;\n" + "\n".join(body)
html = (S / "shell.html").read_text().replace("/*__APP__*/", js)
(D / "index.html").write_text(html)
print("index.html", len(html), "bytes")
