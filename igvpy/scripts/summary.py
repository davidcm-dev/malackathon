"""Merge per-market check logs into one pass/fail report (Markdown + HTML with screenshots and video).

Local: python scripts/summary.py
CI:    python scripts/summary.py artifacts site   (artifacts/<evidence-market>/results/...)
"""
import html
import json
import os
import shutil
import sys
from collections import defaultdict
from pathlib import Path

src = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("site")
out.mkdir(parents=True, exist_ok=True)

roots = [p for p in src.iterdir() if p.is_dir()] if len(sys.argv) > 1 else [Path(".")]
recs = []
for r in roots:
    res = r / "results"
    if not res.exists():
        continue
    for f in res.glob("checks-*.jsonl"):
        recs += [json.loads(l) for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    if (res / "evidence").exists():
        shutil.copytree(res / "evidence", out / "evidence", dirs_exist_ok=True)

groups = defaultdict(list)
for r in recs:
    groups[(r["market"], r["scenario"])].append(r)

md = "# Intelligent Game Validation - results\n\n"
page = ["<!doctype html><meta charset='utf-8'><title>Intelligent Game Validation</title>",
        "<style>body{font:14px system-ui;margin:2rem;max-width:1100px}table{border-collapse:collapse;width:100%;margin-bottom:1rem}"
        "td,th{border:1px solid #ccc;padding:4px 8px;text-align:left}.pass{color:#0a7a2f}.fail{color:#c00;font-weight:600}.info{color:#666}"
        "img{height:150px;margin:4px;border:1px solid #ccc}</style><h1>Intelligent Game Validation</h1>"]
for (market, scenario), rows in sorted(groups.items()):
    ok = all(r["status"] != "fail" for r in rows)
    icon = "✅" if ok else "❌"
    md += f"## {icon} {market} · {scenario}\n\n| Result | Check | Detail |\n|---|---|---|\n"
    page.append(f"<h2>{icon} {market} · {html.escape(scenario)}</h2><table><tr><th>Result</th><th>Check</th><th>Detail</th></tr>")
    for r in rows:
        md += f"| {r['status'].upper()} | {r['name']} | {r['detail'].replace('|', '/')} |\n"
        page.append(f"<tr><td class='{r['status']}'>{r['status'].upper()}</td><td>{html.escape(r['name'])}</td><td>{html.escape(r['detail'])}</td></tr>")
    md += "\n"
    page.append("</table>")
    slug = "".join(c if c.isalnum() else "-" for c in scenario.lower()).strip("-")
    ev = out / "evidence" / market / slug
    if ev.exists():
        for img in sorted(ev.glob("*.png")):
            rel = img.relative_to(out)
            page.append(f"<a href='{rel}'><img src='{rel}' title='{img.name}'></a>")
        if (ev / "video.webm").exists():
            page.append(f"<p><a href='{(ev / 'video.webm').relative_to(out)}'>▶ video.webm</a></p>")
(out / "index.html").write_text("\n".join(page), encoding="utf-8")
(out / "summary.md").write_text(md, encoding="utf-8")
if os.getenv("GITHUB_STEP_SUMMARY"):
    with open(os.environ["GITHUB_STEP_SUMMARY"], "a", encoding="utf-8") as f:
        f.write(md)
print(md)
