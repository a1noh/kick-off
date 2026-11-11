"""Render every mermaid block in docs/plan.md into docs/architecture.html (one card each).

Usage (from the classroom folder):  .venv/bin/python ~/.claude/skills/discovery/templates/render_diagrams.py
Mermaid is pinned to the same major/minor version the VS Code mermaid extension uses, so if it renders here
it renders in the ⇧⌘V preview too. Prints one line per diagram; exit 1 if plan.md has no mermaid blocks.
"""

import html
import re
import sys
from pathlib import Path

MERMAID = "https://cdn.jsdelivr.net/npm/mermaid@11.12.2/dist/mermaid.esm.min.mjs"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
:root{{--bg:#f8fafc;--fg:#0f172a;--muted:#475569;--card:#ffffff;--line:#e2e8f0}}
@media (prefers-color-scheme: dark){{:root:not([data-theme="light"]){{--bg:#0b1120;--fg:#e2e8f0;--muted:#94a3b8;--card:#111827;--line:#1f2937}}}}
:root[data-theme="dark"]{{--bg:#0b1120;--fg:#e2e8f0;--muted:#94a3b8;--card:#111827;--line:#1f2937}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 -apple-system,system-ui,sans-serif}}
main{{max-width:1000px;margin:0 auto;padding:32px 16px}}
h1{{font-size:24px;margin:0 0 4px}} h2{{font-size:18px;margin:28px 0 10px}} p{{color:var(--muted);margin:0 0 8px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:20px;overflow-x:auto}}
</style></head><body><main>
<h1>{title}</h1>
<p>Generated from docs/plan.md — edit the plan, then re-run render_diagrams.py.</p>
{cards}
</main>
<script type="module">
import mermaid from "{mermaid}";
mermaid.initialize({{startOnLoad:true, theme:"default"}});
</script></body></html>
"""


def main() -> int:
    plan = Path("docs/plan.md")
    text = plan.read_text()
    title_match = re.search(r"^# (?:Plan: )?(.+)$", text, re.M)
    title = (title_match.group(1).strip() if title_match else "Agent") + ": architecture"
    cards, n = [], 0
    for m in re.finditer(r"```mermaid\n(.*?)```", text, re.S):
        heading = re.findall(r"^#{2,3} (.+)$", text[: m.start()], re.M)
        n += 1
        label = heading[-1] if heading else f"Diagram {n}"
        cards.append(f'<h2>{html.escape(label)}</h2><div class="card"><pre class="mermaid">\n{m.group(1)}</pre></div>')
        print(f"diagram {n}: {label}")
    if not cards:
        print("no ```mermaid blocks found in docs/plan.md", file=sys.stderr)
        return 1
    out = Path("docs/architecture.html")
    out.write_text(PAGE.format(title=html.escape(title), cards="\n".join(cards), mermaid=MERMAID))
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
