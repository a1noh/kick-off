# Phase N · <name> · spec

Written by `/build` **before any code**. Copy this file to `docs/specs/phase-N/spec.md`.
Rules: every requirement comes from a source (`docs/plan.md`, `notes/raw.md:L<n>`, `data/<file>`), never from intuition.
Anything you can't trace goes to the user as a question, and the answer is recorded under Assumptions.
`scripts/spec.py check` enforces the format (the Stop hook runs it).

## Scope
- **Phase line (verbatim from plan.md):** `- [ ] Phase N: …`
- **On screen (verbatim):** …
- **Not in this phase:** … (what stays 🚧 / ⬜, and which phase fixes it)

## Sources
- plan.md §… · raw.md:L… · data/…

## Interfaces
Exact signatures and record schemas this phase adds or must keep stable:
- `Agent(extract, store).reply(text) -> str`
- `out/<record>.jsonl`: {"field", …}

## Requirements
One block per requirement. Keep each field on **one line**. `Acceptance` has the exact expected value in "quotes".
The screen as the user sees it **after this phase is built and ticked** is a requirement too.

### R1 · <short title>
- Traces to: plan.md §6 Phase N Try it 1 · raw.md:L12
- Acceptance: input `…` → reply "…" · panel … shows "…"
- Test: tests/test_phaseN.py::test_r1_short_title

## Assumptions
- none
<!-- or: - <decision> · confirmed by user 2026-11-10. An unconfirmed line blocks the build. -->

## Verification
Written by `.venv/bin/python scripts/spec.py verify N` into `verify.md` next to this file. Never by hand.
