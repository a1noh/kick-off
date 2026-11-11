<!-- WORKED EXAMPLE (refill-request agent). Shows how templates/architecture.md looks when filled in. Do not copy its labels. -->

## 5. Architecture
> Open the preview to see the diagram: **⇧⌘V** (or the preview icon at the top right of this tab).

```mermaid
flowchart LR
  SMS(["📱 Patient SMS<br/>scripts/demo.py · ui/app.py"])
  GI{{"🛡️ guards.py · GUARD IN<br/>emergency words?"}}
  E911(["🚨 'Call 911' · STOP<br/>no verify · no model"])
  AG["🧠 agent.py · BRAIN<br/>loop + session state<br/>verified? · tries left?"]
  LLM["🤖 Gemini (REST, free tier)<br/>extracts name · DOB · drug as JSON"]
  T["✋ tools.py · HANDS (gated in code)<br/>verify_patient · find_rx<br/>submit_refill · route_to_queue"]
  D[("💾 data.py · MEMORY<br/>clean CSVs · dedupe · parse DOB")]
  Q[("📋 Queue + audit.jsonl<br/>renewal / staff + reason")]
  GO{{"🛡️ guards.py · GUARD OUT<br/>no unverified data<br/>no invented values · no fake success"}}
  R(["💬 Reply to patient"])

  SMS --> GI
  GI -- "emergency" --> E911
  GI -- "safe" --> AG
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
In short, the model only **extracts** (intent, name, DOB, drug). Python makes every decision and writes every reply from templates filled with tool results.

### 5b. Agent loop: who decides what
The same 4 stages as a typical agent, but the LLM owns **only step ①**. Purple = LLM · green = Python.

```mermaid
flowchart LR
  M(["📱 Message"]) --> GI{{"🛡️ Guard in<br/>emergency word?"}}
  GI -- "yes" --> S911(["🚨 'Call 911' · STOP"])
  GI -- "no" --> I["① Intent<br/>🤖 Gemini<br/>→ intent · name · DOB · drug"]
  I --> A["② Tool access<br/>🐍 Python decides<br/>verified? · on their list?<br/>controlled? · refills > 0?"]
  A -- "allowed" --> X["③ Tool execute<br/>🐍 tools.py<br/>re-checks every gate"]
  A -- "not allowed" --> Q[("👩‍⚕️ Staff / 🩺 renewal queue<br/>+ reason")]
  X --> ANS["④ Answer<br/>🐍 template filled<br/>from the tool result"]
  Q --> ANS
  ANS --> GO{{"🛡️ Guard out<br/>values match the data?"}}
  GO --> R(["💬 Reply"])

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
| ② Tool access | LLM picks the tool | **Python decides** | A prompt can be talked into "refill my oxycodone"; an `if` can't |
| ③ Tool execute | Tool runs | **Tool runs and re-checks every gate** | Defense in depth: a bug in ② still can't refill |
| ④ Answer | LLM writes it | **Python template** | It can't invent a drug, pharmacy or pickup time |
