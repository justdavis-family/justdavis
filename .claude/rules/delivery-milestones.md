# Referencing Delivery Milestones

Delivery-plan milestones (M1, M2, …) are a planning device, and plans shift.
References to milestones can rot in two distinct ways:

- *Future* milestone references rot because the plan can be resequenced;
    "this lands in M5" stops being true the moment the work is moved to M4 or M6.
- *Past* and *current* milestone references in long-lived content rot because the *code*
    keeps changing;
    a comment that says "stubbed for M2, real impl in M3"
    stays in the file after a later milestone rewrites the same function,
    and the comment now mis-ascribes the function's behavior to the wrong milestone.

Point-in-time content
  (PR titles, PR descriptions, commit messages)
  doesn't suffer from the second failure mode,
  because it's a record of a single moment and is never re-edited.

## The Rule

### Long-Lived Content — Code, Comments, Project Docs, Design Docs

- Do **not** hard-code specific delivery-milestone identifiers (M2, M3, …)
    in code, code comments / doc-comments, project docs, or design docs.
- Describe *state and intent* instead:
    "stubbed for now", "the real implementation comes later", "a later milestone", etc.
- *General* references to the design docs or the delivery plan are encouraged
    — they stay correct as the plan evolves.
- The delivery plan and its milestone tracking issues are the single source of truth
    for the milestone breakdown;
    link to them rather than restating the list.

#### Exceptions

**The delivery plan itself**, and its milestone tracking issues, are where milestones are
  enumerated — that is the whole point of the document.
`M1`, `M2`, … headings in a delivery plan are expected, not a violation:
  the rule above governs everything that *refers* to the breakdown,
  not the document that *defines* it.

**A project's own `README.md`** may name the **current** milestone
  (for example, to mark "this state"),
  because that describes the present, not a forecast,
  and a README is consciously updated as project state changes.

Future and past milestones still should not be enumerated in long-lived content
  outside those two places.

### Point-in-Time Content — PR Titles/Descriptions, Commit Messages

PRs and commits are records of a specific moment and are never re-edited,
  so the second failure mode (comment-vs.-code drift) doesn't apply.

- Naming the **current** milestone (the one a PR implements) is fine,
    including in the squash-commit subject and body that the PR will produce.
- Naming **past** completed milestones is also fine,
    e.g. "replaces the M2 stub" or "fixes a regression introduced in M4".
- **Future** milestone identifiers are still prohibited
    — those rot the same way they do in long-lived content.
  Describe state and intent: "a later milestone", "as those versions are verified", etc.
