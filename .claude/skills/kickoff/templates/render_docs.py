"""Render the project's Markdown docs (text + mermaid diagrams) to HTML, for when the .md preview can't show diagrams.

  .venv/bin/python scripts/render_docs.py                 docs/talk.md + docs/plan.md -> docs/talk.html + docs/plan.html
  .venv/bin/python scripts/render_docs.py docs/talk.md    just that one

Open the .html in any browser. (On GitHub the .md files already render their mermaid diagrams.)
Mermaid is pinned to the version the VS Code preview uses, so a diagram that renders here renders there too.
"""

import html
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11.12.2/dist/mermaid.esm.min.mjs"
MARKED = "https://cdn.jsdelivr.net/npm/marked@15.0.7/lib/marked.esm.js"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root{{--bg:#f8fafc;--fg:#0f172a;--muted:#475569;--card:#ffffff;--line:#e2e8f0;--code:#f1f5f9}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#0b1120;--fg:#e2e8f0;--muted:#94a3b8;--card:#111827;--line:#1f2937;--code:#1e293b}}}}
:root[data-theme="dark"]{{--bg:#0b1120;--fg:#e2e8f0;--muted:#94a3b8;--card:#111827;--line:#1f2937;--code:#1e293b}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.6 -apple-system,system-ui,sans-serif}}
main{{max-width:960px;margin:0 auto;padding:24px 16px}}
h1{{font-size:26px}} h2{{font-size:20px;margin-top:32px;border-bottom:1px solid var(--line);padding-bottom:4px}}
code{{background:var(--code);padding:1px 5px;border-radius:4px;font-size:14px}}
pre{{background:var(--code);padding:12px;border-radius:8px;overflow-x:auto}} pre code{{padding:0}}
table{{border-collapse:collapse;display:block;overflow-x:auto}} th,td{{border:1px solid var(--line);padding:6px 10px;text-align:left}}
.mermaid{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px;overflow-x:auto}}
.note{{color:var(--muted);font-size:13px}}
</style></head><body><main>
<p class="note">Rendered from {source}. Edit the .md, then re-run scripts/render_docs.py.</p>
<div id="doc">Loading…</div>
</main>
<script type="module">
import {{ marked }} from "{marked}";
import mermaid from "{mermaid}";
const md = {markdown};
const doc = document.getElementById("doc");
doc.innerHTML = marked.parse(md);
doc.querySelectorAll("pre > code.language-mermaid").forEach((code) => {{
  const box = document.createElement("div");
  box.className = "mermaid";
  box.textContent = code.textContent;
  code.parentElement.replaceWith(box);
}});
mermaid.initialize({{ startOnLoad: false, theme: matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "default" }});
await mermaid.run();
</script></body></html>
"""


def render(md_path: Path) -> Path:
    """One .md -> a .html next to it; returns the output path."""
    text = md_path.read_text()
    m = re.search(r"^# (.+)$", text, re.M)
    title = m.group(1).strip() if m else md_path.stem
    out = md_path.with_suffix(".html")
    source = md_path.relative_to(ROOT) if md_path.is_relative_to(ROOT) else md_path
    page = PAGE.format(
        title=html.escape(title),
        source=html.escape(str(source)),
        marked=MARKED,
        mermaid=MERMAID,
        markdown=json.dumps(text).replace("</", "<\\/"),  # safe inside <script>
    )
    out.write_text(page)
    diagrams = len(re.findall(r"^```mermaid$", text, re.M))
    print(f"wrote {out.relative_to(ROOT) if out.is_relative_to(ROOT) else out} ({diagrams} diagram(s))")
    return out


def main(args: list[str]) -> int:
    paths = [Path(a).resolve() for a in args] or [p for p in (ROOT / "docs/talk.md", ROOT / "docs/plan.md") if p.exists()]
    missing = [p for p in paths if not p.exists()]
    if missing or not paths:
        print(f"nothing to render: {missing or 'no docs/talk.md or docs/plan.md'}", file=sys.stderr)
        return 1
    for p in paths:
        render(p)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
