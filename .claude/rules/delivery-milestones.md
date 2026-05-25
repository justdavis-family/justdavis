# Referencing Delivery Milestones

Delivery-plan milestones (M1, M2, …) are a planning device, and plans shift.
A comment or doc that says "this lands in M3" rots the moment the plan is resequenced,
  and nobody remembers to update it.

## The Rule

- Do **not** hard-code specific delivery-milestone identifiers (M2, M3, …)
    in code, comments, or project docs.
- Describe *state and intent* instead:
    "stubbed for now", "the real implementation comes later", "a later milestone", etc.
- *General* references to the design docs or the delivery plan are encouraged
    — they stay correct as the plan evolves.
- The delivery plan and its milestone tracking issues are the single source of truth
    for the milestone breakdown; link to them rather than restating the list.

## Exception

A project's own `README.md` **may** name the **current** milestone
  (for example, to mark "this state"),
  because that describes the present, not a forecast.
Future milestones still should not be enumerated outside the delivery plan and its issues.
