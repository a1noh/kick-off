<!-- TEMPLATE for docs/requirements.md (/discovery writes it before plan.md). WHAT the client needs, never HOW.
No code, no file names, no function names. Every rule and decision is traced: raw.md:L<n>, data/<file>, or
"decided with user <date>". plan.md cites these ids (B1, D1, …) instead of restating them. ~80 lines. -->
# Requirements: ‹product name›

## Problem and success (in the client's words)
- **Problem:** ‹what hurts today, who has it› (raw.md:L‹n›)
- **For:** ‹the end user› · **owner:** ‹who runs it day to day and what they check every morning› (raw.md:L‹n›)
- **Success:** "‹their exact words›" (raw.md:L‹n›)

## Business rules
One line each, numbered, plain English, each with its source. The code must follow every one; tests cite them.
- **B1** ‹rule, e.g. "A customer sees a bike's status only after the ticket and last name match the same row."› · raw.md:L‹n›
- **B2** ‹rule› · data/‹file› (‹the fact in the data›)
- **B3** ‹rule› · decided with user ‹date› (see D1)

## Decisions on the ambiguous points
The notes were silent or unclear here, so we asked. Format: the question · the answer · why.
- **D1** ‹question, e.g. "What do we say when every pickup slot is full?"› · ‹answer› · ‹why› · decided with user ‹date›

## Data facts the rules depend on
- ‹e.g. "repairs.csv has 4 rows; T-102 and T-103 are the same Brompton (duplicate)."› · data/‹file›

## Out of scope (today)
- ‹what we deliberately won't build› · raw.md:L‹n›

## Open questions (ask before the phase that needs them)
- none
