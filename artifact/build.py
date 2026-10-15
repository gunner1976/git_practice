"""Build the two deliverables from the shared sources:
   casing_design.html  - the Claude artifact page (no doctype; the Artifact tool wraps it)
   hub_index.html      - a complete document for the SurCana hub at /pages/casing-design/ (Nexus bar + Planner mode)
"""
import pathlib
a = pathlib.Path(__file__).parent
js = "\n".join((a / f).read_text() for f in ("data.js", "engine.js", "planner_mode.js", "ui.js"))
head = (a / "head.html").read_text()
(a / "casing_design.html").write_text(head + "<script>\n" + js + "\n</script>\n")
hub_head = head.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '').replace(
    '<header><a href="#home">', '<script src="/static/nexus.js" data-tool="casing-design" defer></script>\n<header><a href="#home">')
hub = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
       + hub_head.split('<header>')[0] + '</head>\n<body>\n<header>' + hub_head.split('<header>', 1)[1] + "<script>\n" + js + "\n</script>\n</body>\n</html>\n")
(a / "hub_index.html").write_text(hub)
(a / "_bundle.js").write_text(js)
print("artifact", len(head) + len(js), "bytes; hub", len(hub), "bytes")
