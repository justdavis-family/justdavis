# Process Divergence Across Adopting Repositories

## Question

This repository's development process
  — the `design/` directory's READMEs and templates, the `design-process` skill,
  the agent rules that govern process, the pull-request and issue templates,
  the process-related workflows, and the engineering principles —
  is also followed by one or more other repositories, some of which may be private.
Nothing keeps those copies aligned except occasional manual effort.

Before deciding how to keep them aligned,
  it is worth knowing precisely how far apart they have drifted, and in what ways.
This analysis answers:

1. When did process content last move between this repository and another, and in which direction?
2. Which improvements exist on one side and not the other, in each direction?
3. What shape does the divergence take:
     are files identical, extended, restructured, renamed, or missing?
4. How much of the process content is specific to the repository it sits in?
5. Which elements of the process are consumed from the repository itself,
     and which are pure content that could in principle live anywhere?

Findings compare this repository at commit `b80c62d` (2026-08-18)
  with a checkout of one other adopting repository, taken on 2026-09-04.
File names and line counts are this repository's.
The other repository is described but not named, and none of its content is quoted.

## Findings

### 1. The Last Sync Was Manual, One-Way, and Nearly Five Months Ago

The other repository adopted this repository's process content in April 2026,
  through two pull requests on the same day, by hand.
That is the only time process content has ever moved between the two,
  and it moved outward from this repository only.
A reverse sync, bringing that repository's improvements here,
  was analysed at the time and deferred.
It never happened.

Since mid-April, this repository has merged six pull requests whose subject is the process itself
  (#12, #25, #30, #32, #39, #40),
  plus two project pull requests that added engineering principles along the way (#14, #15).
The three most recent (#32, #39, #40) were each cross-cutting,
  touching between three and twenty files across `design/`, `.claude/`, and `.github/` at once,
  and #40 also re-cased headings in fifteen dated design documents.

*Provenance:* this repository's history is verified from `git log`.
The other repository's dates come from an inventory of its history made for this analysis
  and are inherited here rather than re-verified.

### 2. What Never Propagated, in Each Direction

**Outward** — present here, absent there:

- The `design-process` skill, and the rule that points agents at it.
- The delivery-plan tracking conventions:
    `Delivery Plan` and `Milestone` issue types, sub-issues, and blocked-by sequencing.
  The other repository's issue-workflow rule is 29 lines to this one's 116.
- The pull-request template and all four issue templates.
  The other repository has none of either.
- The delivery-plan template, and the rule on referencing milestones without rot.
- The Change Types vocabulary, the PR-template guidance, and the merge recipe in the PR workflow rule
    (94 lines there, 198 here).
- The Title Case heading rule.
- The single-home consolidation:
    `design/README.md` became the one statement of the design sequence,
    and `engineering-designs/README.md` lost its restatement of it.
- Guidance on when an analysis is warranted and what makes a good one (12 lines there, 36 here).
- Two engineering principles (Least Privilege; Clear, Unambiguous, Easily-Parsed Data Models),
    and wording refinements in five of the eight principles both repositories share.

**Inward** — present there, absent here:

- An engineering principle on centralized configuration.
- A weekly dependency-audit workflow for Rust dependencies.
  This repository has since gained two Rust projects and still has no equivalent.
- A spelling fix in `design/README.md` (`supercede` to `supersede`), still wrong here at line 51.
- A wording fix in the review workflow's prompt ("implementation plans" to "delivery plans"),
    still stale here at line 64 of `.github/workflows/claude-code-review.yml`.

The last two are the most telling.
They are corrections to this repository's own content, made elsewhere,
  and nothing brought them back.

The other repository also uses the process more heavily than this one does:
  it holds 23 dated requirements and 12 analyses to this repository's 3 and 4.
It has never written a delivery plan, and this repository has never written a note.
Process improvements made here are therefore exercised mostly somewhere else,
  and the somewhere else is running the older process.

*Provenance:* verified by `diff` between the two checkouts, and by `ls` of each `design/` subdirectory.

### 3. The Shape of the Divergence

Thirty-four files fall inside the process scope.
Comparing each:

| Shape | Files | Which |
|---|---|---|
| Identical. | 12 | Every `design/*/CLAUDE.md` stub; the engineering-principles README and template; the notes README; the product-vision README and template. |
| Extended here (a superset of the other). | 8 | `design/README.md`; the analyses, delivery-plans, and product-requirements READMEs; the markdown-style, PR-workflow, issue-workflow, and design-process rules. |
| Restructured here. | 1 | `engineering-designs/README.md` is shorter here (70 lines to 86) because its restatement of the sequence moved into `design/README.md`. |
| Cosmetic. | 4 | One heading's case in the engineering-design template; the example URLs in the requirements template; one prompt line in the review workflow; one documentation URL in the mention-responder workflow. |
| Diverged in content. | 1 | The engineering-principles index: each side lists principles the other lacks, and every path differs. |
| Missing there. | 8 | The skill; the milestone-referencing rule; the delivery-plan template; the PR template; the four issue templates. |

Two further shapes hide inside "identical" and "extended":

- **Renamed and edited at once.**
  All eight principles both repositories share were re-dated here
    (from a single December 2025 date to a spread of January 2026 dates),
    so no principle has the same filename on both sides.
  Three of the eight are byte-identical under the new names;
    five also differ in content, by two to thirteen lines.
  A mechanism that tracks identity by path sees eight deletions and ten additions;
    one that tracks by content sees three renames, five rename-plus-edits, and two additions.
- **Content moved between files.**
  #32 moved the PR success-criteria checklists out of the PR-workflow rule
    and into the new PR template.
  #39 moved the description of the design sequence out of `engineering-designs/README.md`
    and into `design/README.md`.
  Syncing either half of such a move on its own produces duplication or loss;
    the files involved only make sense as a unit.

*Provenance:* verified by `cmp` and `diff` across the two checkouts,
  and by `git show --stat` of #32 and #39 in this repository.

### 4. Repository-Specific Content Inside the Process

Very little of the process content refers to the repository it sits in.
Three files, five lines:

| File | Line | What is repository-specific |
|---|---|---|
| `.claude/rules/pr-workflow.md` | 46 | A link to an issue in this repository, tracking label automation. |
| `.github/PULL_REQUEST_TEMPLATE.md` | 39 | An absolute URL into this repository's `design/engineering-principles/`. |
| `design/product-requirements/template.md` | 13, 51 | An example pull-request URL: a placeholder here, the other repository's real URL there. |

Two latent cases are worth recording even though neither bites today:

- Several passages assume a monorepo
    (the opening of `design/README.md`; the PR workflow's reasoning about commit scopes).
  Both current adopters are monorepos, so the prose is true in both;
    a single-project adopter would make it false.
- The other repository carries a local security rule stating that its code is confidential.
  That is local content and correctly stays local,
    but it shows that a repository's local rules can contradict the public process's framing,
    and that "local" must be a first-class category rather than an oversight.

The process content is also densely self-linked:
  28 root-absolute links (`/design/…`, `/.claude/…`) and 49 relative links (`../…`) here.
The skill links only relatively; the rules link only root-absolutely;
  the `design/*/CLAUDE.md` stubs `@`-import paths relative to the repository root.
Any partial move of this content breaks some of those references.

*Provenance:* verified by `grep` over the process content in this repository.

### 5. Consumed from the Repository Versus Pure Content

The process elements split three ways by who reads them and from where:

- **Consumed by GitHub from the repository itself:**
    the PR template, the issue templates, and the workflows.
  GitHub only reads these from `.github/` in the repository they apply to,
    so each adopting repository must hold its own copy whatever else is decided.
- **Consumed by Claude Code from the repository:**
    `.claude/CLAUDE.md`, the path-scoped rules under `.claude/rules/`,
    the `@`-importing `design/*/CLAUDE.md` stubs, and skills under `.claude/skills/`.
  Whether Claude Code can load equivalents from outside the repository is not checked here;
    it is a question for the analysis of mechanisms.
- **Pure content:**
    `design/README.md`, the subdirectory READMEs, the templates, and the principles.
  Humans and agents reach these through links, and nothing but those links requires a particular path.

*Provenance:* the first bullet is inherited from general knowledge of GitHub's conventions;
  the second is inferred from the loading behaviour observed in this repository
  and must be verified before a design rests on it.

## Recommendation

The divergence is large in line count but simple in shape.
Bringing the two repositories back together is mostly a matter of
  the other repository adopting this one's current process content wholesale,
  plus this repository adopting a short list of things from the other.
It is not a merge of two evolved forks, and it should not be planned as one.

Whichever mechanism is chosen, convergence has to decide the following,
  and the decisions belong to a human rather than to the mechanism:

1. **Canonical names and dates for the eight shared principles.**
   This repository's January 2026 dates and the other's single December 2025 date cannot both stand
     if the files are to be the same file.
2. **The centralized-configuration principle:** adopt it here, or leave it local there.
   It is project-agnostic, and the earlier analysis in the other repository recommended adopting it.
3. **The dependency-audit workflow:** adopt an equivalent here, since this repository now has Rust
     projects, or leave it local.
4. **The two textual fixes** (`supersede`; "delivery plans"), which should simply be taken.
5. **The five repository-specific lines** in section 4:
     generalize them, or declare them as points where repositories are allowed to differ.

Two things follow for the design work downstream:

- The unit of sync cannot be the individual file.
  The rename-plus-edit and the cross-file moves in section 3 mean that identity
    lives at the level of the process content as a whole.
- Every adopting repository will hold at least its own `.github/` files,
    so even a design that moves most of the process out of the repository
    still has to keep some of it in every repository.

The newest unpropagated change is this pull request's own amendment
  to `design/product-requirements/README.md`;
  it will be the first thing the eventual mechanism has to carry.

## References

- [Design and Planning Process](../README.md) — the process whose divergence this inventories.
- [Delivery Plans](../delivery-plans/README.md) —
    the tracking conventions that make up the largest single outward gap.
- [Engineering Principles](../engineering-principles/README.md) —
    the document type whose files were renamed and edited at once.
- [Least Privilege](../engineering-principles/2026-05-12-least-privilege.md) and
    [Clear, Unambiguous, Easily-Parsed Data Models](../engineering-principles/2026-05-12-clear-data-models.md) —
    the two principles that exist only here.
