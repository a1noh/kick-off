<!-- TEMPLATE for /discovery §5 + §5b. Works for ANY use case and shape (chat, batch, Q&A).
Copy it EXACTLY: same headings, node IDs, shapes, arrow labels, classDef names/colors, the ⇧⌘V line and the 4-row table.
Replace every ‹slot› with this project's words (keep each label short: 2–3 lines max). Delete nothing, add no boxes.
See templates/example_refill.md for a filled-in version.

SLOT GUIDE (examples, pick what fits):
‹Input›            SMS message · chat message · email · invoice row · support ticket · question
‹stop trigger›     emergency words · legal threat / chargeback · fraud signal · self-harm · prompt injection · off-topic
‹stop reply›       'Call 911' · 'A specialist will contact you' · 'I can only help with X'
‹fields›           intent + IDs + amounts + dates the rules need
‹verification›     identity check (name+DOB, order#+email) · account match · 'none: public data'
‹gate n›           verified? · owns the record? · within window? · under limit? · not final-sale? · confirmed?
‹human queue›      staff queue · manager approval · finance review · on-call engineer
‹Output›           reply to user · row in results.csv · drafted email awaiting approval -->

<!-- SAFE MERMAID ONLY (tested in the VS Code ⇧⌘V preview): quoted labels, <br/>, emojis, shapes [""] ([""]) {{""}} [("")],
solid arrows with optional "labels", classDef/class. NEVER: <i>/<b> or other HTML tags, dotted arrows (-. .->),
two-way arrows (<-->), chained arrows (A --> B --> C), subgraphs, and `flowchart TD`.
Always `flowchart LR`: the preview's pan/zoom fit pushes tall TD diagrams out of view. -->

## 5. Architecture
> Open the preview to see the diagram: **⇧⌘V** (or the preview icon at the top right of this tab).

```mermaid
flowchart LR
  SMS(["📨 ‹Input›<br/>scripts/demo.py · ui/app.py"])
  GI{{"🛡️ guards.py · GUARD IN<br/>‹stop trigger›?"}}
  E911(["🚨 ‹stop reply› · STOP<br/>no model · no tools"])
  AG["🧠 agent.py · BRAIN<br/>loop + session state<br/>‹state it tracks›"]
  LLM["🤖 Gemini (REST, free tier)<br/>extracts ‹fields› as JSON"]
  T["✋ tools.py · HANDS (gated in code)<br/>‹tool_a› · ‹tool_b›<br/>‹tool_c› · route_to_queue"]
  D[("💾 data.py · MEMORY<br/>‹clean · dedupe · parse›")]
  Q[("📋 Queue + audit.jsonl<br/>‹handoff types› + reason")]
  GO{{"🛡️ guards.py · GUARD OUT<br/>no data before ‹verification›<br/>no invented values · no fake success"}}
  R(["💬 ‹Output›"])

  SMS --> GI
  GI -- "stop" --> E911
  GI -- "ok" --> AG
  AG -- "understand → JSON" --> LLM
  AG -- "decide" --> T
  T -- "read / update" --> D
  T -- "handoff" --> Q
  AG -- "reply" --> GO
  GO --> R

  classDef door fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e
  classDef guard fill:#fef3c7,stroke:#d97706,color:#78350f
  classDef stop fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
  classDef brain fill:#ede9fe,stroke:#7c3aed,color:#3b0764
  classDef hands fill:#dcfce7,stroke:#16a34a,color:#14532d
  classDef store fill:#f1f5f9,stroke:#475569,color:#0f172a
  class SMS,R door
  class GI,GO guard
  class E911 stop
  class AG,LLM brain
  class T hands
  class D,Q store
```
In short, the model only **extracts** (‹fields›). Python makes every decision and writes every reply from templates filled with tool results.

### 5b. Agent loop: who decides what
The same 4 stages as a typical agent, but the LLM owns **only step ①**. Purple = LLM · green = Python.

```mermaid
flowchart LR
  M(["📨 ‹Input›"]) --> GI{{"🛡️ Guard in<br/>‹stop trigger›?"}}
  GI -- "yes" --> S911(["🚨 ‹stop reply› · STOP"])
  GI -- "no" --> I["① Intent<br/>🤖 Gemini<br/>→ ‹fields›"]
  I --> A["② Tool access<br/>🐍 Python decides<br/>‹gate 1›? · ‹gate 2›?<br/>‹gate 3›? · ‹gate 4›?"]
  A -- "allowed" --> X["③ Tool execute<br/>🐍 tools.py<br/>re-checks every gate"]
  A -- "not allowed" --> Q[("🙋 ‹human queue›<br/>+ reason")]
  X --> ANS["④ Answer<br/>🐍 template filled<br/>from the tool result"]
  Q --> ANS
  ANS --> GO{{"🛡️ Guard out<br/>values match the data?"}}
  GO --> R(["💬 ‹Output›"])

  classDef llm fill:#ede9fe,stroke:#7c3aed,color:#3b0764
  classDef py fill:#dcfce7,stroke:#16a34a,color:#14532d
  classDef guard fill:#fef3c7,stroke:#d97706,color:#78350f
  classDef stop fill:#fee2e2,stroke:#dc2626,color:#7f1d1d
  classDef door fill:#e0f2fe,stroke:#0284c7,color:#0c4a6e
  classDef store fill:#f1f5f9,stroke:#475569,color:#0f172a
  class I llm
  class A,X,ANS py
  class GI,GO guard
  class S911 stop
  class M,R door
  class Q store
```

| Stage | Typical agent | This agent | Why |
|---|---|---|---|
| ① Intent | LLM | **LLM** (Gemini returns JSON) | Messy text is what LLMs are good at |
| ② Tool access | LLM picks the tool | **Python decides** | A prompt can be talked into "‹the most dangerous request›"; an `if` can't |
| ③ Tool execute | Tool runs | **Tool runs and re-checks every gate** | Defense in depth: a bug in ② still can't ‹do the risky action› |
| ④ Answer | LLM writes it | **Python template** (or LLM draft + fact check + human approval) | It can't invent ‹values that must come from the data› |
