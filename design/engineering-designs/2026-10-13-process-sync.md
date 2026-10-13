# Process Sync Engineering Design

## Overview

This design delivers the six requirements under
  [One Development Process across Many Repositories](../product-vision/2026-09-04-design-process-sync.md):
  [Propose a Process Sync](../product-requirements/2026-09-06-process-sync-proposal.md),
  [Apply a Process Sync Proposal](../product-requirements/2026-09-06-process-sync-apply.md),
  [Remember Sync Decisions](../product-requirements/2026-09-08-sync-decisions.md),
  [Unattended Sync Proposals](../product-requirements/2026-10-04-unattended-sync-proposals.md),
  [Publish Approved Outbound Changes](../product-requirements/2026-10-04-publish-outbound-changes.md),
  and [Enroll a New Repository](../product-requirements/2026-10-12-enrolling-a-repository.md).
It rests on two analyses:
  [Process Divergence across Adopting Repositories](../analyses/2026-09-04-process-divergence-inventory.md),
  which measured what the sync has to carry,
  and [Keeping the Development Process in Sync across Repositories](../analyses/2026-10-12-cross-repo-process-sync.md),
  which chose the shape and is not re-argued here.

The technical problem is to keep a self-linked set of process files
  — the `design/` READMEs and templates, the engineering principles, the design-process skill,
  the process rules under `.claude/rules/`, the `design/*/CLAUDE.md` stubs,
  and the templates and workflows under `.github/` —
  identical across repositories that are otherwise unrelated, have different owners,
  and may be private,
  while never storing a credential that reaches from one repository into another
  and never letting anything forwarded from another repository run before a human has chosen to
  run it.

The analysis settled the shape, and this design takes it as given:

- The process stays in every repository as replicated files; nothing is installed from elsewhere.
- A skill, itself process content, does the explaining and grouping;
    deterministic tools do the comparing, checking, and delivering, and need no agent.
- Each following repository runs the sync in its own workflow with its own `GITHUB_TOKEN` only.
  Inbound pull requests are created with that token on purpose,
    so GitHub parks their workflow runs until a human approves them.
- Outbound changes leave only by a maintainer's hand, after an approval recorded in the working
  repository.
- Workflow files cross as patch files that a maintainer applies.
- The topology is a hub: followers pull from the public repository, which runs nothing on their
  behalf and knows none of them.

## Technology Choices

### The Skill: `process-sync`

The agent-facing entry point is a Claude Code skill at `.claude/skills/process-sync/SKILL.md`,
  with supporting files for the proposal format and the grouping heuristics.
It is shared process content like the `design-process` skill beside it, and it is thin:
  it runs the deterministic tools, reads both histories, classifies and groups the differences,
  writes the proposal and the pull-request and approval-request texts,
  and hands everything else to the tools.
The agent never holds a credential and never pushes:
  it writes files into an output directory, and a tool delivers them.

Rationale: a skill is the only mechanism that travels with the process, loads in every
  repository that holds it, and can be invoked both by a maintainer in a session and by
  `claude-code-action` in a workflow.

### The Deterministic Tools: Python Standard Library, as mise File Tasks

The comparison, the reference check, delivery, publication, and enrollment are Python 3 scripts
  using only the standard library, placed under `mise-tasks/process/` so that
  [mise discovers them as file tasks](https://mise.jdx.dev/tasks/file-tasks.html)
  named `process:compare`, `process:check-refs`, `process:deliver`, `process:publish`,
  and `process:enroll`, with `process:test` running their tests.
A file's path below `mise-tasks/` is its task name, so the tasks need no entry in `mise.toml`,
  which the manifest classifies as local by design;
  the directory travels as process content and works unchanged in any repository that uses mise.
Shared code sits in a non-executable package beside the scripts, which mise does not list as tasks.

Rationale: the tools must run as files, unchanged, in every following repository and in its CI,
  with no build step, no download, and no dependency the repository does not already have.
Python 3.11 or later is on every GitHub-hosted runner and on every developer machine here,
  and its standard library covers TOML, JSON, subprocess, and difflib,
  which is everything the tools need.
Rust, the monorepo's application language, would need a toolchain or a published binary in every
  follower, and a published binary is a supply-chain surface the sync should not have.
Shell would make the manifest parsing and the reference scanning fragile.

### Manifest, Local Values, and Decisions: TOML under `design/process-sync/`

The boundary manifest, each repository's local values, and each repository's decisions log are
  TOML files in a `design/process-sync/` directory, beside a README that is the human
  documentation of the sync.
TOML carries comments, which the manifest and the log need, and parses with the standard library.

Rationale: the manifest and the log are read by humans deciding what is process content and why
  a repository differs, and by tools that must not guess.
One format that both can read, in the directory where the process is documented,
  keeps the definition in one place.

### Unattended Runs: GitHub Actions and `claude-code-action`

A single workflow, `.github/workflows/process-sync.yml`, shared verbatim and human-applied,
  runs the comparison daily and on demand in every following repository.
When the comparison reports differences it runs the skill through
  [`claude-code-action`](https://github.com/anthropics/claude-code-action),
  authenticated to Claude by the same OAuth token the review workflow uses,
  and then delivers what the skill produced with `GITHUB_TOKEN`.

Rationale: this is the one mechanism that runs in the follower, needs no credential for the hub,
  and creates pull requests whose workflow runs GitHub parks until a human approves them.

### Outbound Publication: By Hand, through the Same Tools

A maintainer publishes an approved outbound change by running `process:publish` in a checkout
  of the counterpart, with their own `gh` authorization.
No automation holds a credential for the counterpart, now or in this design;
  the analysis names the App-only shape that could replace this if volume ever justified it.

## Architecture

### Where Everything Lives

| Path | Class | Holds |
|---|---|---|
| `design/process-sync/README.md` | Shared. | How to run a sync, read a proposal, respond to what a run creates, approve and publish, and enroll. |
| `design/process-sync/manifest.toml` | Shared. | The boundary manifest. |
| `design/process-sync/local.toml` | Local. | This repository's visibility, its counterpart, and its value for every variation point. |
| `design/process-sync/decisions.toml` | Local. | This repository's decisions log. |
| `design/process-sync/pending/` | Local. | Carriers for human-applied units, present only on a sync branch until a maintainer applies them. |
| `.claude/skills/process-sync/` | Shared. | `SKILL.md`, `proposal-format.md`, and `grouping.md`. |
| `mise-tasks/process/` | Shared. | The five tasks, their tests, and the package they share. |
| `.github/workflows/process-sync.yml` | Shared, human-applied. | The unattended run. |

Adding `design/process-sync/` is the one structural change to `design/`;
  its README explains itself and `design/README.md` gains a line pointing at it.

### Data Flow of a Run

Every run, attended or not, has the same four stages, and the agent is present in only one.

1. **Compare.**
   `process:compare` reads the manifest and both repositories' local values and decisions,
     normalizes both sides, and reports one status per entry.
   If every status is identical, declined, or accepted, the run ends here and creates nothing.
2. **Propose.**
   The skill reads the comparison, both histories, and both decisions logs,
     classifies each difference, groups the differences into units, drafts each unit's text,
     and writes a proposal plus one directory per unit into an output directory.
   It writes nothing else.
3. **Confirm.**
   Attended, the maintainer reads the proposal, regroups, answers or defers the decisions it
     raises, and asks for delivery, having seen exactly what will be created.
   Unattended, there is no one to ask: units that need a decision are turned into questions,
     and the rest go to delivery as they are.
4. **Deliver.**
   `process:deliver` turns each inbound unit into a branch and a pull request in the working
     repository, and each outbound unit into an approval request there, or prints what it would do.

### The Comparison

`process:compare --counterpart <path> [--here <ref>] [--there <ref>] [--json]`.

- Both sides are read with `git show <ref>:<path>` from the two checkouts, never from the
    working trees; `--here` defaults to `HEAD` and `--there` to the counterpart's default branch.
  The resolved commit of each side, and whether each working tree is dirty, are in the output.
- Normalization replaces each repository's own value for a variation point with the placeholder
    `{{name}}` before comparing, so a declared difference is invisible.
- A decision of kind `renamed` pairs the counterpart's path with this repository's path,
    so a file the two sides name differently compares as one entry rather than as two missing ones.
- Each entry gets exactly one status:
    `identical`, `differs`, `missing-here`, `missing-there`, `declined`, `accepted`, or `error`.
  A manifest path that exists on neither side, a variation point with no local value,
    a carrier left in `pending/` on the compared ref, and any failure to read are `error`,
    never `identical`, per
    [Clear, Unambiguous, Easily-Parsed Data Models](../engineering-principles/2026-05-12-clear-data-models.md).
- The exit code is `0` when nothing differs, `1` when something does, and `2` on any error,
    so a workflow can branch on it without parsing the output.
- The counterpart is only read, through its checkout;
    nothing in this tool talks to GitHub.

### The Reference Check

`process:check-refs [--find <path>]` scans every manifest entry present in the repository,
  plus the files under the two skills, for Markdown links, `@`-imports, and skill pointers,
  resolving relative links against the linking file, root-absolute links against the repository
  root, and `@` paths against the importing file, as Claude Code does.
Every target that does not exist is reported with its file and line, and the exit code is `1`.
With `--find`, it instead lists every file in the repository, local content included,
  that refers to the given path, which is how a rename's references are found for updating.

### Explaining and Grouping Differences

The skill classifies each `differs` or `missing` entry from history, using
  `git log --follow` on each side, `git diff -M` between the two contents,
  and `git log -S` for content moved between files, and labels it
  edit, addition, removal, rename, rename plus edit, or move.
For each it names the commits on the side that changed, and the pull requests those commits name.

Grouping follows `grouping.md`, which the first milestone writes with these starting heuristics
  and which is expected to evolve with use:

- Mirror the upstream pull requests by default: one unit per upstream pull request that still
    has an effect, carrying that pull request's own summary.
- Collapse upstream pull requests whose later one fully supersedes the earlier one's lines.
- Split an upstream pull request only when its parts touch disjoint files, each part is
    independently reviewable, and the split lowers the net burden; say so in the proposal.
- Never separate the two halves of a rename or a move.
- A unit that needs a human decision is its own unit, so the rest are not held up by it.
- A unit touching a human-applied entry carries that entry as a patch and says why.

### The Proposal

The proposal is a Markdown document in the shape `proposal-format.md` fixes:
  the two sides and their commits; the comparison table; one section per unit with its
  direction, files, classification, provenance, draft title and description, and any decision it
  needs; the grouping rationale; the human-applied items; and the list of decisions cited from
  the log.
The counterpart appears only as the path the maintainer supplied.
Attended, it is written where the maintainer asks, default a scratch directory;
  unattended, it is the run's artifact and its summary.

Beside the proposal, the skill writes one directory per unit:

```
out/
  proposal.md
  units/<id>/
    unit.toml      # id, direction, type, title, base ref, files, provenance, human_applied
    body.md        # pull-request description (inbound) or approval-request body (outbound)
    *.patch        # git format-patch series: the commits the unit consists of
```

The unit id is a hash of the unit's files and the commits it draws from,
  so the same unit has the same id on every run, which is what makes delivery idempotent.
The patches are authored as the working repository's branch will carry them:
  the working repository's own variation values substituted, local references to renamed
  content updated, and the commit message holding the provenance the apply requirement calls for.
When the working repository is public and the content came from a private counterpart,
  the message and the body say only that the change was synced from another repository that
  follows this process, unless the maintainer chose otherwise in the confirm stage.

### Delivery: Branches, Pull Requests, and Approval Requests

`process:deliver <out> [--dry-run] [--units <id>,...]` runs with whatever `gh` authorization
  the caller has: the maintainer's own in a session, `GITHUB_TOKEN` in the workflow.

For an inbound unit it creates the branch `<type>/sync-<slug>` from the unit's base ref,
  applies the patches with `git am`, pushes, and opens a pull request titled per the
  repository's conventions whose body is the unit's text followed by the repository's
  pull-request template sections and an HTML comment marker holding the unit id.
A later run finds an existing pull request by that marker,
  updates its branch with `--force-with-lease` and its body when the unit's content changed,
  and closes it with a comment when the comparison no longer reports the unit.
Nothing it creates is labeled; the maintainer applies `claude-review` or not.

For a human-applied entry, the patch for that file is committed on the branch at
  `design/process-sync/pending/<unit-id>-<name>.patch` instead of being applied,
  and the body says so.
The maintainer applies it with `git am` and deletes it in the same commit before merging;
  the comparison reports one left on the compared ref as an error.

For an outbound unit it pushes the unit's commits to `sync-out/<slug>` in the working repository
  and opens or updates an issue of type `Task` titled `Sync out: <title>`, whose body holds
  the proposed pull-request title and description for the counterpart,
  the complete diff in a fenced block, the branch and its commit,
  a content hash over the diff, the human-applied items the maintainer must carry by hand,
  and the one sentence that records an approval: a comment reading `Approved <hash>`.
If the diff would exceed the issue body limit, the body holds the first part and links the
  branch's compare view for the rest.
A later run with changed content updates the body and hash and comments that the earlier
  approval has lapsed; a run whose comparison no longer reports the unit closes the issue
  saying where the content now stands.

A failure in any stage of the unattended run opens or updates one issue,
  `Process sync failed`, found by its marker, with a link to the run;
  it is never silent, per [Fail Fast and Loud](../engineering-principles/2026-01-09-fail-fast.md).

### Approval and Publication

`process:publish <private-checkout> <issue-number> [--dry-run]` runs in a checkout of the
  counterpart, by a maintainer.

1. It reads the approval request through `gh` in the working repository and checks that the
     latest `Approved <hash>` comment is by a user with write permission there,
     that the hash matches the body's current hash, and that the `sync-out/` branch head matches
     the commit the body names.
   Any mismatch stops it: the approval has lapsed and a new one is needed.
2. It shows the exact diff it is about to publish and waits for the maintainer's `yes`.
3. It creates `<type>/sync-<slug>` in the counterpart from the counterpart's default branch,
     applies the patches from the `sync-out/` branch with `git am`,
     pushes with the maintainer's authorization, and opens the pull request with the title and
     body the approval request showed.
   The commits and the body name no private repository, ref, or commit unless the approver
     put them there.
4. It comments on the approval request with the counterpart pull request's URL.
   Run again for the same approval, it finds that comment and creates nothing.

The counterpart's own review follows; publishing applies no label, approves nothing,
  and merges nothing.
When the content later lands in the counterpart, the working repository's next unattended run
  sees it in sync and closes the approval request.
A refused request, or a change the counterpart turned down,
  is recorded in the decisions log as `declined`, so the next proposal does not raise it again.

### The Decisions Log

`decisions.toml` holds an array of decisions, each with a date, a kind, the paths it concerns,
  what was decided, why, who decided, and the decision it supersedes if any.
The kinds are the four the requirement names:
  `declined` (the comparison reports the path as `declined`),
  `resolved` (a conflict settled; the proposal cites it and carries the resolution to the other
  side rather than raising the conflict),
  `renamed` (the canonical name; the comparison pairs the two paths),
  and `accepted` (a permanent variation; the comparison reports `accepted`).
The skill appends a decision to the log in the same unit that carries it out, never on its own;
  revisiting one adds a new entry naming the old one, and the old one stays.
A public repository's log describes content and reasons and never names a private counterpart;
  the skill refuses to write a counterpart's name, ref, or commit into a public log.

### Enrollment

`process:enroll <path-to-new-repository>` runs in a checkout of the hub and copies the sync
  tooling into the new repository's working tree: the task directory, the skill, the manifest,
  the README, the workflow file, and skeleton `local.toml` and `decisions.toml`.
It writes to a working tree only; the maintainer commits.
The rest is a sync: in the new repository, `local.toml` is filled in, the skill is run with the
  hub as counterpart, and the proposal is applied.
A repository holding none of the process content gets one unit, so one pull request;
  one that already holds some gets whatever the grouping heuristics produce,
  with every conflict put to the maintainer and recorded.
Nothing in the hub changes, and the hub learns nothing.

## Configuration

### The Manifest

Every process file is listed by path; nothing is process content by implication,
  and a local rule, principle, or skill beside a shared one needs no entry.
Directories are never entries, which is what lets local additions sit beside shared files.

```toml
# design/process-sync/manifest.toml — shared verbatim; the boundary of the process.

[[entry]]
path = "design/README.md"
class = "shared"

[[entry]]
path = "design/product-requirements/template.md"
class = "shared"
variations = ["example_pr_url"]   # {{example_pr_url}} is this repository's value in local.toml

[[entry]]
path = "design/engineering-principles/2026-01-06-yagni.md"
class = "shared"

[[entry]]
path = ".github/workflows/claude-code-review.yml"
class = "shared"
human_applied = true              # carried as a patch, applied by a maintainer

[[entry]]
path = "design/process-sync/local.toml"
class = "local"                   # listed so no reader assumes it is shared

[[entry]]
path = "CONTRIBUTING.md"
class = "local"
```

### Local Values

```toml
# design/process-sync/local.toml — local by design; never synced.

[repository]
visibility = "private"            # checked against GitHub when a tool can reach it

[counterpart]
url = "https://github.com/justdavis-family/justdavis.git"
default_branch = "main"           # omit the table entirely in the hub, which follows no one

[variations]
example_pr_url = "https://github.com/example/example/pull/1"
```

The hub's file declares `visibility = "public"` and no counterpart,
  so its copy of the workflow runs the comparison stage, finds nothing to compare, and stops.

### The Decisions Log

```toml
# design/process-sync/decisions.toml — local by design; never synced.

[[decision]]
date = "2026-11-01"
kind = "renamed"
paths = ["design/engineering-principles/2026-01-06-yagni.md"]
decided = "This repository adopts the counterpart's name and date for this principle."
reason = "One canonical name lets the comparison pair the files; the content was identical."
by = "maintainer"
supersedes = ""
```

### The Workflow

The workflow is four jobs, so that the agent's job holds nothing it could write with.

```yaml
# .github/workflows/process-sync.yml — shared verbatim; human-applied.
name: Process Sync
on:
  schedule:
    - cron: "17 6 * * *"          # daily; well inside the vision's one-week bound
  workflow_dispatch:
concurrency:
  group: process-sync
  cancel-in-progress: false
jobs:
  compare:
    permissions: { contents: read }
    # Check out this repository with full history, read local.toml, check out the
    # counterpart (public, so no token) with full history, run process:compare --json,
    # and expose its exit status as a job output.
  propose:
    needs: compare
    if: needs.compare.outputs.status == 'differs'
    permissions: { contents: read }
    # Run claude-code-action with github_token set to the read-only GITHUB_TOKEN, the
    # prompt invoking the process-sync skill unattended, --allowed-tools limited to
    # reading, git log/show/diff, mise run process:*, and writing under out/, and
    # --max-turns bounded; upload out/ as an artifact.
  deliver:
    needs: propose
    permissions: { contents: write, pull-requests: write, issues: write }
    # Download out/, run process:deliver out/ with GITHUB_TOKEN.
  report-failure:
    needs: [compare, propose, deliver]
    if: failure()
    permissions: { issues: write }
    # Open or update the "Process sync failed" issue with a link to this run.
```

Two points of this layout are deliberate.
The agent runs in a job whose token can only read, and the action is handed that token
  explicitly rather than minting its own, so that even an agent that ignored its tool allowance
  could create nothing.
Delivery runs in a separate job with `GITHUB_TOKEN`, so that every branch and pull request it
  creates has the parked workflow runs the analysis relies on;
  no stronger token is ever introduced for the inbound direction.
The first unattended milestone confirms that the action accepts a read-only `GITHUB_TOKEN` in
  this mode; if it does not, the fallback is the action's own token with an allowance that
  excludes every write, which is weaker and would be recorded as such.

### Repository Settings and Secrets

In every following repository:

- The Actions setting "Allow GitHub Actions to create and approve pull requests" is on.
  It is one checkbox covering both abilities; the sync needs only the first.
- `CLAUDE_CODE_OAUTH_TOKEN` is present, as it already is for the review workflow.
- The ruleset on the default branch stays as it is;
    the sync creates branches and pull requests and never merges.
- Python 3.11 or later and mise are available, as the enrollment README states.

In the hub, before the first implementation milestone, per the analysis:
  the `@`-imports are fixed ([#44](https://github.com/justdavis-family/justdavis/issues/44)),
  and the admin bypass on `main` is changed from "always" to "for pull requests only".
The hub holds no secret and no setting for the sync.

## Trade-Offs

- **Python over Rust.**
  Gained: no build, no toolchain, no published artifact, and a follower needs nothing new.
  Sacrificed: the monorepo's Rust conventions and typed errors;
    the tools compensate with explicit status values and a non-zero exit on every failure.
- **TOML and Python 3.11.**
  Gained: comments in the manifest and the log, and standard-library parsing.
  Sacrificed: a follower on an older Python must install one, which mise makes a one-line step.
  JSON would remove the prerequisite and the comments with it; the comments were worth more.
- **File tasks over `mise.toml` entries.**
  Gained: the tasks travel as files and `mise.toml` stays local.
  Sacrificed: a follower that does not use mise runs the scripts directly, which the README
    shows; nothing else about them needs mise.
- **The agent writes files; a tool delivers them.**
  Gained: the agent holds no credential, delivery is deterministic and tested,
    and the attended and unattended paths share one delivery code path and one dry run.
  Sacrificed: two extra jobs and an artifact in the workflow, and the agent cannot react to a
    delivery failure in the same run; the failure issue covers that.
- **Outbound by hand.**
  Gained: no cross-repository credential exists anywhere.
  Sacrificed: the outbound direction's bounded time rests on a maintainer acting on an open
    approval request; the analysis names the App shape to adopt if that ever fails in practice.
- **A daily no-op run in the hub.**
  Gained: the workflow file is shared verbatim, with no hub-specific variant to maintain.
  Sacrificed: a short daily run in the hub that compares nothing.
- **Markers in bodies rather than labels.**
  Gained: the issue-workflow rule's label vocabulary stays as it is, and a unit's identity is
    the content hash rather than a label anyone can apply.
  Sacrificed: finding sync pull requests in a list means searching the body marker,
    which the README documents.
- **A single counterpart per repository.**
  Gained: one `[counterpart]` table, one workflow, and the hub topology the analysis chose.
  Sacrificed: a private repository cannot sync directly with another;
    it reaches it through the hub, which the analysis judged strictly safer.
- **No sync of the hub from a follower.**
  Gained: the hub runs nothing and knows no follower.
  Sacrificed: nothing automated ever writes to the hub;
    every change to it is a pull request a human opened.

## Success Criteria

- `process:test` passes, building its fixture repositories with `git init` at test time
  and covering: two converged repositories (exit `0`, nothing reported);
  an edit, an addition, a removal, a rename, a rename plus edit, and a move,
  each reported with the right status;
  a variation point substituted on both sides; a `renamed` decision pairing two paths;
  a `declined` decision reported as `declined`; a missing manifest path and a missing local
  value reported as `error` with exit `2`; a dirty working tree reported and excluded;
  and the reference check catching a dangling link, a dangling `@`-import, and a dangling skill
  pointer.
- `process:deliver --dry-run` on a sample output directory prints every branch, pull request,
  and approval request it would create and creates nothing; run for real and then again,
  the second run creates nothing and reports what exists.
- A pull request created by the unattended run in a following repository shows its workflow runs
  parked until a maintainer approves them.
- A full unattended run in a following repository against a converged hub creates nothing;
  against a hub with one merged process change, it opens one pull request carrying that change
  within one day.
- `process:publish --dry-run` against an approval whose hash no longer matches the content
  refuses; against a valid approval it shows the exact diff and, after `yes`, opens one pull
  request in the counterpart whose body names no private repository.
- Neither repository holds any credential for the other, before or after the first milestones:
  the only secrets in a follower are those the review workflow already needs.
- The hub's `.github/workflows/process-sync.yml` runs and creates nothing,
  and the hub's content and history contain no follower's name.
- `process:check-refs` passes in the hub after the `@`-import fix, and fails on a fixture with
  one of the ten root-relative imports restored.
- Enrolling a scratch repository with `process:enroll` and one sync yields one pull request,
  after which the comparison between it and the hub reports everything identical apart from
  declared variations.

## References

- **Product Requirements**:
  [Propose a Process Sync](../product-requirements/2026-09-06-process-sync-proposal.md),
  [Apply a Process Sync Proposal](../product-requirements/2026-09-06-process-sync-apply.md),
  [Remember Sync Decisions](../product-requirements/2026-09-08-sync-decisions.md),
  [Unattended Sync Proposals](../product-requirements/2026-10-04-unattended-sync-proposals.md),
  [Publish Approved Outbound Changes](../product-requirements/2026-10-04-publish-outbound-changes.md),
  and [Enroll a New Repository](../product-requirements/2026-10-12-enrolling-a-repository.md).
- **Analyses**:
  [Process Divergence across Adopting Repositories](../analyses/2026-09-04-process-divergence-inventory.md)
  and [Keeping the Development Process in Sync across Repositories](../analyses/2026-10-12-cross-repo-process-sync.md).
- **Engineering Principles**:
  [Least Privilege](../engineering-principles/2026-05-12-least-privilege.md),
  which the job layout and the by-hand outbound path follow;
  [Clear, Unambiguous, Easily-Parsed Data Models](../engineering-principles/2026-05-12-clear-data-models.md),
  which the comparison's seven statuses follow;
  [Fail Fast and Loud](../engineering-principles/2026-01-09-fail-fast.md),
  which the exit codes and the failure issue follow;
  [Mocks Are Usually Dumb](../engineering-principles/2026-01-15-avoid-mocks.md),
  which is why the tests build real repositories;
  and [YAGNI](../engineering-principles/2026-01-06-yagni.md),
  which is why there is one counterpart, no App, and no registry.
