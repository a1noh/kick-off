<!-- TEMPLATE for /discovery §5 + §5b when the kind is APP (no AI, or AI as one optional helper).
Copy it EXACTLY: same headings, node IDs, shapes, arrow labels, classDef names/colors, the ⇧⌘V line and the 4-row table.
Replace every ‹slot› with this project's words (keep each label short: 2–3 lines max). Delete nothing, add no boxes.
If the plan has one AI helper (e.g. "parse a free-text request into a booking"), keep node H and fill it in;
if there is no AI at all, set H's label to "🧩 no AI helper<br/>all input is structured" (keep the node: same diagram every time).

SLOT GUIDE (examples, pick what fits):
‹Input›            booking form · filter + date range · uploaded CSV · new ticket · button click
‹bad input›        missing field · wrong format · date in the past · unknown ID · file too big
‹fix-it reply›     'Pick a date from tomorrow on' · 'Column "amount" is missing' · 'That ID does not exist'
‹rules›            slot free? · within opening hours? · under capacity? · user allowed? · state change allowed?
‹actions›          book_slot · cancel · approve · move_state · export_csv
‹records›          bookings · tickets · approvals · results
‹blocked queue›    needs-approval list · conflicts list · errors to fix
‹Output›           confirmation + updated calendar · filtered chart + table · ticket in its new state -->

<!-- SAFE MERMAID ONLY (tested in the VS Code ⇧⌘V preview): quoted labels, <br/>, emojis, shapes [""] ([""]) {{""}} [("")],
solid arrows with optional "labels", classDef/class. NEVER: <i>/<b> or other HTML tags, dotted arrows (-. .->),
two-way arrows (<-->), chained arrows (A --> B --> C), subgraphs, and `flowchart TD`.
Always `flowchart LR`: the preview's pan/zoom fit pushes tall TD diagrams out of view. -->

## 5. Architecture
> Open the preview to see the diagram: **⇧⌘V** (or the preview icon at the top right of this tab).

```mermaid
flowchart LR
  IN(["🖱️ ‹Input›<br/>app.py · demo.py"])
  GI{{"🛡️ guards.py · CHECK IN<br/>‹bad input›?"}}
  FIX(["✋ ‹fix-it reply› · STOP<br/>nothing saved"])
  CO["⚙️ core.py · LOGIC<br/>one request end to end<br/>‹rules›"]
  H["🤖 optional AI helper<br/>‹what it turns into fields›"]
  T["✋ tools.py · ACTIONS (gated in code)<br/>‹actions›"]
  D[("💾 data.py · MEMORY<br/>‹records› · clean · dedupe")]
  Q[("📋 ‹blocked queue› + audit.jsonl<br/>+ reason")]
  GO{{"🛡️ guards.py · CHECK OUT<br/>result matches the data?<br/>no fake success"}}
  R(["📊 ‹Output›"])

  IN --> GI
  GI -- "bad" --> FIX
  GI -- "ok" --> CO
  CO -- "free text → fields" --> H
  CO -- "decide" --> T
  T -- "read / update" --> D
  T -- "blocked" --> Q
  CO -- "result" --> GO
  GO --> R

  classDef door fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e
  classDef guard fill:#fef3c7,stroke:#d97706,color:#78350f
  classDef stop fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
  classDef brain fill:#ede9fe,stroke:#7c3aed,color:#3b0764
  classDef hands fill:#dcfce7,stroke:#16a34a,color:#14532d
  classDef store fill:#f1f5f9,stroke:#475569,color:#0f172a
  class IN,R door
  class GI,GO guard
  class FIX stop
  class H brain
  class CO,T hands
  class D,Q store
```
In short, every rule is plain Python in `core.py` + `tools.py`; the screen only shows what the records say.

### 5b. One request: who decides what
Purple = AI (optional helper only) · green = Python.

```mermaid
flowchart LR
  M(["🖱️ ‹Input›"]) --> GI{{"🛡️ Check in<br/>‹bad input›?"}}
  GI -- "yes" --> FIX(["✋ ‹fix-it reply› · STOP"])
  GI -- "no" --> I["① Read the request<br/>🐍 form fields, or 🤖 helper<br/>→ ‹fields›"]
  I --> A["② Rules<br/>🐍 Python decides<br/>‹rule 1›? · ‹rule 2›?<br/>‹rule 3›?"]
  A -- "allowed" --> X["③ Action<br/>🐍 tools.py<br/>re-checks every rule"]
  A -- "not allowed" --> Q[("🙋 ‹blocked queue›<br/>+ reason")]
  X --> ANS["④ Result<br/>🐍 built from the records"]
  Q --> ANS
  ANS --> GO{{"🛡️ Check out<br/>matches the data?"}}
  GO --> R(["📊 ‹Output›"])

  classDef llm fill:#ede9fe,stroke:#7c3aed,color:#3b0764
  classDef py fill:#dcfce7,stroke:#16a34a,color:#14532d
  classDef guard fill:#fef3c7,stroke:#d97706,color:#78350f
  classDef stop fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
  classDef door fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e
  classDef store fill:#f1f5f9,stroke:#475569,color:#0f172a
  class I llm
  class A,X,ANS py
  class GI,GO guard
  class FIX stop
  class M,R door
  class Q store
```

| Stage | Typical quick app | This app | Why |
|---|---|---|---|
| ① Read | Trust the form | **Check in first** (‹bad input›) | Bad input is caught before anything is saved |
| ② Rules | Scattered in the UI code | **One place: core.py** | Easy to test, easy to show on stage |
| ③ Action | Writes straight away | **Re-checks every rule** | A UI bug still can't ‹do the risky action› |
| ④ Result | Whatever the code returns | **Built from the saved records** | The screen can't show something that didn't happen |
