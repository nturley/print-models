"""Assemble a static site from every design that has a build/report.json.

    uv run python -m scadcheck.site _site

Layout (matches the viewer's relative `../<design>/build/` paths):
    _site/index.html                  list of designs with test status
    _site/viewer/index.html
    _site/<design>/build/report.json
    _site/<design>/build/<part>.stl
"""

from __future__ import annotations

import html
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Print Models</title>
<style>
  :root {{ --bg:#f6f6f4; --panel:#fff; --ink:#1d1f23; --muted:#6b7078; --line:#e2e2de; --pass:#2f8f5b; --fail:#c4423a; --accent:#3a6ea5; color-scheme: light; }}
  @media (prefers-color-scheme: dark) {{ :root {{ --bg:#16181b; --panel:#1e2125; --ink:#e6e7e9; --muted:#969ba3; --line:#2e3237; --pass:#4cb67d; --fail:#e2645b; --accent:#6fa0d6; color-scheme: dark; }} }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font:14px/1.5 system-ui, sans-serif; }}
  main {{ max-width:720px; margin:0 auto; padding:40px 16px; }}
  h1 {{ font-size:22px; margin:0 0 4px; }}
  p {{ color:var(--muted); margin:0 0 24px; }}
  a {{ color:var(--accent); }}
  .card {{ position:relative; display:flex; align-items:center; gap:16px; padding:14px 16px; margin-bottom:8px;
    background:var(--panel); border:1px solid var(--line); border-radius:8px; }}
  .card:hover {{ border-color:var(--accent); }}
  .card a.name {{ font-weight:600; color:inherit; text-decoration:none; }}
  .card a.name::after {{ content:""; position:absolute; inset:0; }}  /* whole card opens the viewer */
  .card a.src {{ position:relative; z-index:1; font-size:13px; }}
  .status {{ margin-left:auto; font-size:13px; }}
  .ok {{ color:var(--pass); }} .bad {{ color:var(--fail); }}
</style>
</head>
<body><main>
<h1>Print Models</h1>
<p>Design checks for 3D-printable OpenSCAD models. Built {generated}.{repo}</p>
{cards}
</main></body>
</html>
"""


def find_reports() -> list[Path]:
    """Every <design>/build/report.json in the repo, including nested designs
    (e.g. board-game-inserts/root). Skips hidden folders, virtualenvs and the site output."""
    found = []
    for dirpath, dirnames, filenames in os.walk(ROOT):
        here = Path(dirpath)
        if here.name == "build":
            if "report.json" in filenames:
                found.append(here / "report.json")
            dirnames[:] = []
            continue
        dirnames[:] = [d for d in dirnames if not (d.startswith((".", "_")) or d.endswith("venv") or d in ("node_modules", "viewer"))]
    return sorted(found)


def build(out: Path) -> list[str]:
    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(ROOT / "viewer", out / "viewer")
    cards, names, repo_url = [], [], None
    reports = find_reports()
    for report_path in reports:
        design = report_path.parent.parent.relative_to(ROOT).as_posix()
        report = json.loads(report_path.read_text(encoding="utf-8"))
        dest = out / design / "build"
        dest.mkdir(parents=True)
        shutil.copy2(report_path, dest / "report.json")
        files = [part["stl"] for part in report["parts"]]
        files += [part["print_stl"] for part in report["parts"] if part.get("print_stl")]
        files += [d["file"] for d in report.get("downloads", [])]
        for f in files:
            (dest / f).parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(report_path.parent / f, dest / f)
        tests = report["tests"]
        failed = sum(t["outcome"] not in ("passed", "skipped") for t in tests)
        status = f'<span class="bad">{failed} of {len(tests)} failing</span>' if failed else f'<span class="ok">{len(tests)} passing</span>'
        repo = report.get("repo")
        source = (
            f'<a class="src" href="{html.escape(repo["url"])}/tree/{repo["ref"]}/{html.escape(design)}">source</a>'
            if repo else ""
        )
        cards.append(
            f'<div class="card"><a class="name" href="viewer/?design={html.escape(design)}">{html.escape(design)}</a>'
            f'<span class="status">{status}</span>{source}</div>'
        )
        repo_url = repo_url or (repo and repo["url"])
        names.append(design)
    generated = max((json.loads(p.read_text(encoding="utf-8"))["generated"] for p in reports), default="")
    repo_line = (
        f' Source: <a href="{html.escape(repo_url)}">{html.escape(repo_url.removeprefix("https://"))}</a>.' if repo_url else ""
    )
    (out / "index.html").write_text(
        PAGE.format(
            cards="\n".join(cards) or "<p>No designs have test reports yet.</p>",
            generated=generated.replace("T", " "),
            repo=repo_line,
        ),
        encoding="utf-8",
    )
    (out / ".nojekyll").touch()
    return names


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "_site").resolve()
    print("built", out, "with", build(out))
