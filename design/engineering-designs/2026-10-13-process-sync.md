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

The technical problem is to keep the generally applicable parts of one repository's development
  process identical in every repository that follows it,
  where the repositories are otherwise unrelated, have different owners, and may be private,
  while never storing a credential that reaches from one repository into another
  and never letting anything forwarded from another repository run before a human has chosen to
  run it.
Most of that content is whole files:
  the `design/` READMEs and templates, the engineering principles, the design-process skill,
  the process rules under `.claude/rules/`, the `design/*/CLAUDE.md` stubs,
  and the templates and workflows under `.github/`.
Some of it is a part of a file whose remainder belongs to the repository it sits in:
  a paragraph of the repository-wide agent brief, the body of a conventions rule that each
  repository extends, the shape of the pre-commit hook.
The design handles both, and prefers the first wherever a file can be split so that it fits.

The analysis settled the shape, and this design takes it as given:

- The process stays in every repository as replicated files; nothing is installed from elsewhere.
- The topology is a hub: followers pull from the public repository, which runs nothing on their
    behalf and knows none of them.
  The hub offers; each follower declares what it adopts and how its copy differs,
    and holds everything about itself.
- A skill, itself process content, does the explaining and grouping;
    deterministic tools do the comparing, checking, and delivering, and need no agent.
- Each follower runs the sync in its own workflow with its own `GITHUB_TOKEN` only.
  Inbound pull requests are created with that token on purpose,
    so GitHub parks their workflow runs until a human approves them.
- Outbound changes leave only by a maintainer's hand, after an approval recorded in the follower.
- Workflow files cross as patch files that a maintainer applies.

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
  using only the standard library, placed under `mise-tasks/process-sync/` so that
  [mise discovers them as file tasks](https://mise.jdx.dev/tasks/file-tasks.html)
  named `process-sync:compare`, `process-sync:check-refs`, `process-sync:deliver`, `process-sync:publish`,
  and `process-sync:enroll`, with `process-sync:test` running their tests.
A file's path below `mise-tasks/` is its task name, so the tasks need no entry in `mise.toml`,
  which stays each repository's own;
  the directory travels as process content and works unchanged in any repository that uses mise.
Shared code sits in a non-executable package beside the scripts, which mise does not list as tasks.

Rationale: the tools must run as files, unchanged, in every follower and in its CI,
  with no build step, no download, and no dependency the repository does not already have.
Python 3.11 or later is on every GitHub-hosted runner and on every developer machine here,
  and its standard library covers TOML, JSON, regular expressions, subprocess, and difflib,
  which is everything the tools need.
Rust, the monorepo's application language, would need a toolchain or a published binary in every
  follower, and a published binary is a supply-chain surface the sync should not have.
Shell would make the manifest parsing and the reference scanning fragile.

### Catalog and Manifest: TOML under `.process-sync/`

The hub's catalog of what it offers, each follower's manifest of what it adopts,
  and the README that documents the sync for humans live in a top-level `.process-sync/`
  directory.

Rationale for the place: the sync's scope is the whole repository, not the design process alone,
  so it belongs beside `.github/`, `.githooks/`, and `.claude/`, the other repository-wide tooling
  homes, rather than under `design/`, whose subdirectories are document types.
The skill's directory is the agent's entry point and nothing else;
  the tools must not depend on an agent vendor's directory to find their data.

Rationale for TOML: the standard library parses it, so the tools need nothing installed;
  each record is a self-delimited table, so a pull request that changes the manifest shows whole
  records and indentation cannot change meaning in review;
  and the repository already speaks TOML for mise, Cargo, and pyproject,
  and YAML only where GitHub requires it.
YAML would read a little shorter and cost one dependency.

### Unattended Runs: GitHub Actions and `claude-code-action`

A single workflow, `.github/workflows/process-sync.yml`, shared verbatim and applied by hand,
  runs the comparison daily and on demand in every follower.
When the comparison reports differences it runs the skill through
  [`claude-code-action`](https://github.com/anthropics/claude-code-action),
  authenticated to Claude by the same OAuth token the review workflow uses,
  and then delivers what the skill produced with `GITHUB_TOKEN`.
The workflow is the by-hand sequence in
  [Running the Sync by Hand](#running-the-sync-by-hand) executed on a schedule;
  nothing happens in a job that the sequence cannot do from a terminal.

Rationale: this is the one mechanism that runs in the follower, needs no credential for the hub,
  and creates pull requests whose workflow runs GitHub parks until a human approves them.

### Outbound Publication: By Hand, through the Same Tools

A maintainer publishes an approved outbound change by running `process-sync:publish` in a checkout
  of the hub, with their own `gh` authorization.
No automation holds a credential for the hub, now or in this design;
  the analysis names the App-only shape that could replace this if volume ever justified it.

## Architecture

### Where Everything Lives

| Path | Held by | Holds |
|---|---|---|
| `.process-sync/README.md` | Every repository; shared. | The one explanation of the sync: how to run it by hand, read a proposal, respond to what a run creates, approve and publish, and enroll. |
| `.process-sync/catalog.toml` | The hub only. | What the hub offers, with suggested regions and replacements where relevant. |
| `.process-sync/manifest.toml` | Each follower only. | What this repository adopts, how its copies differ, what it declines, and why. |
| `.process-sync/diverge/` | A follower, as needed. | Patch files the manifest names as divergences. |
| `.process-sync/pending/` | A follower, on a sync branch. | Carriers for workflow-file changes, present only until a maintainer applies them. |
| `.claude/skills/process-sync/` | Every repository; shared. | `SKILL.md`, `proposal-format.md`, and `grouping.md`. |
| `mise-tasks/process-sync/` | Every repository; shared. | The five tasks, their tests, and the package they share. |
| `.github/workflows/process-sync.yml` | Every repository; shared, applied by hand. | The unattended run. |

The README is the single home of explanation.
The skill, the workflow, the task scripts, and the comments in the catalog and the manifest
  point to it rather than restating it.
Each repository's `CONTRIBUTING.md`, which documents its directory structure,
  gains a line pointing at the directory; that line is local content, as the whole file is.

### The Catalog and the Manifest

The hub's catalog lists the paths the hub suggests a follower adopt.
A suggestion may also carry the regions of a file the hub expects a follower to want
  and the replacements it expects a follower to need, with the follower's value left blank.
Suggestions are advisory; the catalog never says anything about any follower.

A follower's manifest is the only thing the comparison obeys.
It names the hub, and then lists what the follower adopts and what it declines:

- **An adopted entry** names the hub's path as `source`, and `path` when the follower's copy is
    named differently, which is how a rename is recorded.
  With no `region`, the whole file is adopted.
  With one or more `region` entries, each a `start` and an `end` matcher, only those parts are:
    the follower's file is its own, and the regions inside it are the hub's.
  Regions must be non-overlapping and in order.
  A `diverge` says how the follower's copy departs from the hub's text:
    `diverge.replace` is a list of pairs, each replacing one match with the follower's value;
    `diverge.patch` names a patch file under `.process-sync/diverge/` for anything larger.
  Every matcher, and every `from` of a replacement, is a literal string
    or a table `{ regex = "…" }`, and must match exactly once in the file it is applied to;
    zero or several matches is an error, not a guess.
- **A declined entry** names a suggested path the follower does not want, with a `reason`,
    and optionally `as_of`, the hub commit the decline was decided against.

Which to use for a file that mixes the hub's text with the follower's own:
  when the hub's text is most of the file, the follower adopts the file and diverges;
  when the follower's text is most of the file, it adopts regions.
Both are declarations the follower makes, in one place, about what it takes from the hub;
  the hub owns nothing inside a follower.
Where a file can instead be split so that each part is wholly one side's,
  the split is preferred, because a whole file needs no matcher:
  a general paragraph of the agent brief becomes a rule, which loads the same way;
  a pre-commit hook becomes one shared line that runs a task the repository defines;
  a conventions rule becomes a shared body and a local companion rule, since rules compose.
The skill may propose a split, a region, or a divergence for any file;
  a human decides, and the manifest records.

### Data Flow of a Run

Every run, attended or not, has the same four stages, and the agent is present in only one.

1. **Compare.**
   `process-sync:compare` reads the follower's manifest, clones or fetches the hub, reads the hub's
     catalog from the hub's ref, and reports one status per entry.
   If no status is `differs`, `missing-here`, `missing-there`, or `suggested`,
     the run ends here and creates nothing.
2. **Propose.**
   The skill reads the comparison and both histories,
     classifies each difference, groups the differences into units, drafts each unit's text,
     and writes a proposal plus one directory per unit into an output directory.
   It writes nothing else.
3. **Confirm.**
   Attended, the maintainer reads the proposal, regroups, answers the decisions it raises,
     and asks for delivery, having seen exactly what will be created.
   Unattended, there is no one to ask: a unit that needs a decision is held back whole and
     becomes a question, and the rest go to delivery as they are.
4. **Deliver.**
   `process-sync:deliver` turns each inbound unit into a branch and a pull request in the follower,
     each held unit into a question, and each outbound unit into an approval request,
     or prints what it would do.

### Running the Sync by Hand

The README walks a maintainer through the four stages from a terminal, one command per step,
  each the same command the workflow runs:

1. In the follower, `mise run process-sync:compare`, which reads the hub from the manifest;
     `--counterpart` overrides it with a path or URL, and `--here` and `--there` choose refs.
2. In a Claude Code session there, invoke the `process-sync` skill on the comparison's output,
     and answer the decisions it raises; it writes the proposal and the units under `out/`.
3. Read `out/proposal.md`.
4. `mise run process-sync:deliver out/ --dry-run`, then the same without `--dry-run`,
     which uses the maintainer's own `gh` authorization.
5. For an outbound unit, read the approval request it opened, comment the approval,
     and in a checkout of the hub run `mise run process-sync:publish <follower-checkout> <issue>`.

This sequence is delivered first and proven by converging this repository and its first
  follower by hand; the workflow automates it afterwards and is tested by running both and
  comparing what each produced.

### The Comparison

`process-sync:compare [--counterpart <path-or-url>] [--here <ref>] [--there <ref>] [--json]`.

- The counterpart is a local checkout or a URL.
  A URL is cloned once, read-only, into a cache directory outside the repository,
    with blobs fetched on demand so the full history is available for provenance,
    and fetched on later runs.
  Cloning the public hub needs no credential; a private counterpart, which only an attended run
    would name, uses whatever authorization the maintainer's git already has.
  In the workflow the comparison job clones the hub this way rather than through a second
    checkout step, so the two paths through the tool are one.
- Both sides are read with `git show <ref>:<path>`, never from a working tree;
    `--here` defaults to `HEAD` and `--there` to the hub's default branch.
  The resolved commit of each side, and whether the follower's working tree is dirty,
    are in the output.
- For each adopted entry, the tool takes the hub's file at `source` and the follower's at `path`,
    extracts each region from both with the same matchers or takes both files whole,
    applies the entry's divergence to the hub's side, and compares the pair.
- Each entry gets exactly one status:
    `identical`, `differs`, `missing-here`, `missing-there`, `suggested`, `declined`, or `error`.
  `missing-here` is an adopted file absent in the follower, or a region whose start matcher
    does not match there; `missing-there` is an adopted source the hub no longer has;
    `suggested` is a catalog entry the follower neither adopts nor declines.
  A matcher that matches more or fewer than once, a patch that does not apply,
    a carrier left in `pending/` on the compared ref, and any failure to read are `error`,
    never `identical`, per
    [Clear, Unambiguous, Easily-Parsed Data Models](../engineering-principles/2026-05-12-clear-data-models.md).
- A declined entry with `as_of` is still `declined`, and the output notes when the hub's file has
    changed since that commit, so the proposal can list it for renewal.
- The exit code is `0` when nothing differs, `1` when something does, and `2` on any error,
    so a workflow can branch on it without parsing the output.
- A repository with a catalog and no manifest is a hub; the tool says so and exits `0`.
- Run unattended, which the workflow signals with an environment variable, the tool refuses any
    counterpart other than the manifest's hub and refuses to clone: the clone must already exist.
  This backs up the agent's tool allowance, described in
    [What the Agent May Run](#what-the-agent-may-run).
- Nothing in this tool talks to GitHub beyond cloning.

### The Reference Check

`process-sync:check-refs [--find <path>]` scans every file the manifest names,
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
It reads commit messages and content, which reached the hub's default branch through review,
  and never pull-request bodies or issue comments, which anyone can write and an author can edit
  after merge.

The manifest describes state, never history: a follower's content is the hub's content plus its
  declared divergences, however far behind it is.
So the skill finds where each adopted entry stands in the hub's history rather than being told,
  in this order:

1. **Provenance.**
   Every commit the sync creates names the hub commit it carries,
     so `git log` on the follower's copy finds the hub commit it was last synced from.
2. **Content match.**
   Before the first sync, or after an edit by hand, there is no provenance;
     the skill takes the most recent hub commit whose normalized content equals the follower's.
3. **Nearest version.**
   If nothing matches, the follower changed the file beyond its declared divergences;
     the skill takes the hub version with the smallest diff as the base and treats the remainder
     as the follower's own change, which is an outbound unit or a conflict for a human.

The backlog for the entry is every hub commit after that base that touched it,
  grouped by the pull requests those commits name.
A follower that took one hub change and skipped the next, on the same file,
  holds content no hub version matches; that is a divergence, recorded as a patch,
  not a history the manifest has to keep.

Grouping follows `grouping.md`, which the first milestone writes with these starting heuristics
  and which is expected to evolve with use:

- Mirror the upstream pull requests by default: one unit per upstream pull request that still
    has an effect, carrying that pull request's own summary.
- Collapse upstream pull requests whose later one fully supersedes the earlier one's lines.
- Split an upstream pull request only when its parts touch disjoint files, each part is
    independently reviewable, and the split lowers the net burden; say so in the proposal.
- Never separate the two halves of a rename or a move.
- Never regroup to isolate a decision.
  A unit that needs one is answered whole, attended, or held whole, unattended;
    one open decision delaying the rest of its unit is the right trade, since it was one change.
- A unit touching a workflow file carries that file as a patch and says why.

### The Proposal

The proposal is a Markdown document in the shape `proposal-format.md` fixes:
  the two sides and their commits; the comparison table; one section per unit with its
  direction, files, classification, provenance, draft title and description, and any decision it
  needs, each with a recommendation and the manifest entry that would record it;
  the grouping rationale; the workflow-file items; suggestions not yet adopted;
  and declines whose hub file changed since their `as_of`.
It shows the text a matcher matched, never only the matcher.
The counterpart appears only as the path or URL the maintainer supplied.
Attended, it is written where the maintainer asks, default a scratch directory;
  unattended, it is the run's artifact and its summary.

Beside the proposal, the skill writes one directory per unit:

```
out/
  proposal.md
  units/<id>/
    unit.toml      # id, direction, type, title, base ref, files, provenance, open decisions
    body.md        # pull-request description (inbound) or approval-request body (outbound)
    *.patch        # git format-patch series: the commits the unit consists of
```

The unit id is a hash of the unit's files and the commits it draws from,
  so the same unit has the same id on every run, which is what makes delivery idempotent.
The patches are authored as the follower's branch will carry them:
  the hub's text with the follower's divergences put back, a region written in place inside the
  follower's own file, local references to renamed content updated,
  the manifest edit that records any decision the unit carries out,
  and the commit message holding the provenance the apply requirement calls for.
When the follower is public and the content came from a private counterpart,
  the message and the body say only that the change was synced from another repository that
  follows this process, unless the maintainer chose otherwise in the confirm stage.

### Delivery: Branches, Pull Requests, Questions, and Approval Requests

`process-sync:deliver <out> [--dry-run] [--units <id>,...]` runs with whatever `gh` authorization
  the caller has: the maintainer's own in a session, `GITHUB_TOKEN` in the workflow.

For an inbound unit it creates the branch `<type>/sync-<slug>` from the unit's base ref,
  applies the patches with `git am`, pushes, and opens a pull request titled per the
  repository's conventions whose body is the unit's text followed by the repository's
  pull-request template sections and an HTML comment marker holding the unit id.
A later run finds an existing pull request by that marker,
  updates its branch with `--force-with-lease` and its body when the unit's content changed,
  and closes it with a comment when the comparison no longer reports the unit.
Nothing it creates is labeled; the maintainer applies `claude-review` or not.

Any adopted path under `.github/workflows/` is never written by the tool.
The workflow's own token cannot push a change to a workflow file,
  and a workflow is code that runs on the next event, so a human applies it deliberately.
The patch for that file is committed on the branch at `.process-sync/pending/<unit-id>-<name>.patch`
  instead, and the body says so.
The maintainer applies it with `git am` and deletes it in the same commit before merging;
  the comparison reports one left on the compared ref as an error.

For a held unit, one whose decisions are open, it opens or updates one issue of type `Task`
  titled `Sync decision: <title>`, found by its marker, carrying each decision with its
  recommendation and the exact manifest entry that would record it.
The maintainer records the decision through an ordinary pull request or an attended run;
  the next run finds it in the manifest, closes the question, and delivers the unit whole.

For an outbound unit it pushes the unit's commits to `sync-out/<slug>` in the follower
  and opens or updates an issue of type `Task` titled `Sync out: <title>`, whose body holds
  the proposed pull-request title and description for the hub,
  the complete diff in a fenced block, the branch and its commit,
  a content hash over the diff, the workflow-file items the maintainer must carry by hand,
  and the one sentence that records an approval: a comment reading `Approved <hash>`.
If the diff would exceed the issue body limit, the body holds the first part and links the
  branch's compare view for the rest.
A later run with changed content updates the body and hash and comments that the earlier
  approval has lapsed; a run whose comparison no longer reports the unit closes the issue
  saying where the content now stands.

A failure in any stage of the unattended run opens or updates one issue,
  `Process sync failed`, found by its marker, with a link to the run;
  it is never silent, per [Fail Fast and Loud](../engineering-principles/2026-01-09-fail-fast.md).

### What the Deliver Tool Trusts

The output directory is untrusted input, whoever wrote it.
The tool is deterministic and holds the line between the agent's free text and anything that
  could act:

- It writes only paths the manifest adopts, and refuses a unit naming any other path.
- It never writes under `.github/workflows/`, as above.
- Branch names come from a fixed pattern and the unit's slug, never from the body.
- The pull-request body is the repository's template with the unit's text inserted as content;
    nothing in it is interpreted.
- Everything it creates is a pull request whose workflow runs are parked,
    or an issue, and a human reads both before anything else happens.

So a fully subverted agent yields a reviewable pull request confined to process paths,
  and nothing else.
The human review of that pull request, which the vision requires, is the defense against
  injection; the job layout below only guarantees the agent holds nothing it could act with.

### What the Agent May Run

The agent's job holds the Claude OAuth token, because the action needs it to reach Claude,
  and the agent reads text that anyone could have written, so the rule for its tool allowance is:

**No tool the agent may run accepts a network destination as an argument,
  because any such tool is an exfiltration channel for the token.**
An instruction planted in a commit message could have the agent run such a tool with the token
  spliced into the URL; the shell would expand it, the server named would log it,
  and no scan of the output directory would ever see it, since nothing was written.

So the allowance is: reading files; `git log`, `git show`, and `git diff` on the two local clones;
  `process-sync:check-refs`; and writing under the output directory.
The comparison tool, which can clone, is not in the allowance:
  a plain step clones the hub and runs the comparison before the agent starts,
  and the tool itself refuses to clone when run unattended.
Nothing in the allowance can fetch, clone, push, or open a connection,
  and a reviewer can check any later change to the allowance against the rule in one reading.

The allowance is a check on command text, and checks of that kind have had published bypasses,
  so it is not the only layer.
Before the agent starts, the job blocks all outbound traffic from the runner except to
  Anthropic's API, so that a command which slips past the allowance reaches nowhere.
The agent needs no other destination: the hub is already cloned, and delivery is another job.
The block is a plain step that sets the runner's own firewall rules, preferred over a published
  hardening action for the same reason the design avoids published binaries;
  the milestone that builds the workflow may choose the action if the plain step proves brittle,
  and records why.
Which hosts the agent's job actually reaches, including whatever the action touches while
  installing Claude Code, is found by running once in an audit mode that logs connections,
  not assumed; after that, everything else is blocked.
The two layers are independent: the allowance stops the agent from trying,
  and the block stops a try from succeeding.

What no mechanism catches is a reviewer in a follower approving a subtly bad process change,
  such as a rule that tells agents to do something they should not.
That is the trust extended to any reviewed dependency,
  bounded here by process content being prose and configuration a human reads.

### Approval and Publication

`process-sync:publish <follower-checkout> <issue-number> [--dry-run]` runs in a checkout of the
  hub, by a maintainer.

1. It reads the approval request through `gh` in the follower and checks that the
     latest `Approved <hash>` comment is by a user with write permission there,
     that the hash matches the body's current hash, and that the `sync-out/` branch head matches
     the commit the body names.
   Any mismatch stops it: the approval has lapsed and a new one is needed.
2. It shows the exact diff it is about to publish and waits for the maintainer's `yes`.
3. It creates `<type>/sync-<slug>` in the hub from the hub's default branch,
     applies the patches from the `sync-out/` branch with `git am`,
     pushes with the maintainer's authorization, and opens the pull request with the title and
     body the approval request showed.
   The commits and the body name no private repository, ref, or commit unless the approver
     put them there.
4. It comments on the approval request with the hub pull request's URL.
   Run again for the same approval, it finds that comment and creates nothing.

The hub's own review follows; publishing applies no label, approves nothing, and merges nothing.
When the content later lands in the hub, the follower's next unattended run
  sees it in sync and closes the approval request.
A refused request, or a change the hub turned down,
  is recorded in the follower's manifest as a divergence or a decline,
  so the next proposal does not raise it again.

### Decisions Live in the Manifest

The decisions the requirement names are manifest entries, and the manifest's git history is the
  log:

- A **decline** is a `[[decline]]` entry with its reason.
- A **canonical name** is an adopted entry whose `path` differs from its `source`.
- An **accepted variation** is a `diverge` on an adopted entry.
- A **resolved conflict** is the content itself; the commit that recorded it says why.

When and by whom each was decided is what `git log` on the manifest answers,
  so entries carry no date or author.
A decline alone silences future reports about its path, so it may carry `as_of`, the hub commit
  it was decided against; the comparison notes when the hub's file has changed since,
  and renewing the decline is updating `as_of`.
The skill edits the manifest in the same unit that carries out the decision, never on its own.
A public repository's catalog or manifest never names a private repository;
  the skill refuses to write a private counterpart's name, ref, or commit into one.

### Enrollment

`process-sync:enroll <path-to-new-repository>` runs in a checkout of the hub and copies the sync
  tooling into the new repository's working tree: the task directory, the skill,
  the README, the workflow file, and a manifest that names the hub and adopts every suggestion
  in the catalog, suggested regions and replacements included, with each replacement's value left
  for the maintainer to fill.
It writes to a working tree only; the maintainer edits the manifest, deleting or declining what
  the repository does not want, and commits.
The rest is a sync: in the new repository, the skill is run with the hub as counterpart,
  and the proposal is applied.
A repository holding none of the process content gets one unit, so one pull request;
  one that already holds some gets whatever the grouping heuristics produce,
  with every conflict put to the maintainer and recorded.
Nothing in the hub changes, and the hub learns nothing.

## Configuration

### The Catalog

```toml
# .process-sync/catalog.toml — in the hub only. See .process-sync/README.md.
# Each entry is a suggestion; a follower's manifest says what it actually adopts.

[[suggest]]
path = "design/README.md"

[[suggest]]
path = "design/engineering-principles/2026-01-06-yagni.md"

[[suggest]]
path = ".claude/rules/pr-workflow.md"
# This file names the issue tracking label automation in this repository; yours differs.
replace = [{ from = "/issues/34", to = "", why = "Your label-automation issue." }]

[[suggest]]
path = ".claude/CLAUDE.md"
# Only the evergreen-content guidance is general; the rest of the brief is each repository's own.
region = [
  { start = "**Important**: Keep `CLAUDE.md` files evergreen;",
    end = { regex = 'not transient project state\.$' } },
]

[[suggest]]
path = ".github/workflows/process-sync.yml"
```

### The Manifest

```toml
# .process-sync/manifest.toml — in each follower. See .process-sync/README.md.

hub = "https://github.com/justdavis-family/justdavis.git"

[[adopt]]
source = "design/README.md"

[[adopt]]
source = "design/engineering-principles/2026-01-06-yagni.md"
path = "design/engineering-principles/2025-12-15-yagni.md"    # kept this repository's name

[[adopt]]
source = ".claude/rules/pr-workflow.md"
diverge.replace = [{ from = "/issues/34", to = "/issues/7" }]

[[adopt]]
source = ".claude/CLAUDE.md"
region = [
  { start = "**Important**: Keep `CLAUDE.md` files evergreen;",
    end = { regex = 'not transient project state\.$' } },
]

[[adopt]]
source = ".claude/rules/mise-conventions.md"
diverge.patch = ".process-sync/diverge/mise-conventions.patch"  # adds the Swift and Cargo lines

[[adopt]]
source = ".github/workflows/process-sync.yml"

[[decline]]
path = ".github/ISSUE_TEMPLATE/milestone.md"
reason = "Milestones are tracked outside GitHub here."
as_of = "b80c62d"
```

### The Workflow

The workflow is four jobs, so that the agent's job holds nothing it could write with.

```yaml
# .github/workflows/process-sync.yml — shared verbatim; applied by hand.
# Each job is one step of the by-hand sequence in .process-sync/README.md.
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
    # Check out this repository with full history and without persisting credentials;
    # run process-sync:compare --json, which clones the hub itself; expose the exit status as a
    # job output. A hub, having no manifest, stops here.
  propose:
    needs: compare
    if: needs.compare.outputs.status == 'differs'
    permissions: { contents: read }
    # In a plain step, before the agent starts: clone the hub from the manifest's URL and run
    # process-sync:compare --json, so the agent works on two local clones and clones nothing.
    # Then block all outbound traffic from the runner except to Anthropic's API.
    # Then run claude-code-action with github_token set to the read-only GITHUB_TOKEN, the
    # prompt invoking the process-sync skill unattended, --allowed-tools limited to
    # reading, git log/show/diff on the clones, process-sync:check-refs, and writing under out/,
    # and --max-turns bounded. Fail if any file under out/ contains the Claude OAuth token.
    # Upload out/ as this run's artifact, retained for one day; the deliver job downloads it.
  deliver:
    needs: propose
    permissions: { contents: write, pull-requests: write, issues: write }
    # Download out/ from this run, and run process-sync:deliver out/ with GITHUB_TOKEN.
  report-failure:
    needs: [compare, propose, deliver]
    if: failure()
    permissions: { issues: write }
    # Open or update the "Process sync failed" issue with a link to this run.
```

Jobs share nothing: each runs on a fresh machine, job outputs are strings capped at one
  megabyte, and the only other channel is an artifact, a set of files uploaded at the end of one
  job and downloaded at the start of another, scoped to the run.
The proposal and its units can exceed a megabyte, so they travel as an artifact.
Known abuses of artifacts, and what this workflow does about each:

- Poisoning across workflows, where a privileged workflow downloads an artifact an untrusted
    one produced: the deliver job downloads only from its own run, and the current artifact
    actions scope downloads to the run and make artifacts immutable.
- Secrets in artifacts, where a job uploads a workspace holding a token and anyone with read
    access downloads it: only `out/` is uploaded, the checkout persists no credential,
    retention is one day, and the propose job fails before uploading if any output file contains
    the OAuth token's value.
- Cache poisoning: the workflow uses no Actions cache.
- Path traversal through crafted artifact names: action versions are pinned and artifacts come
    from the same run.

Two points of the layout are deliberate.
The agent runs in a job whose token can only read, and the action is handed that token
  explicitly rather than minting its own, so that even an agent that ignored its tool allowance
  could create nothing.
Delivery runs in a separate job with `GITHUB_TOKEN`, so that every branch and pull request it
  creates has the parked workflow runs the analysis relies on;
  no stronger token is ever introduced for the inbound direction.
The split is a privilege boundary, not an injection defense;
  [What the Deliver Tool Trusts](#what-the-deliver-tool-trusts) is where the agent's output is
  contained, [What the Agent May Run](#what-the-agent-may-run) is what keeps the token from
  leaving the runner, and human review is where injection is caught.
The first unattended milestone confirms that the action accepts a read-only `GITHUB_TOKEN` in
  this mode; if it does not, the fallback is the action's own token with an allowance that
  excludes every write, which is weaker and would be recorded as such.
The repository's mention-responder workflow, which reads comments from anyone,
  is far more exposed than this one; it is outside this design and noted for the hub's hardening.

### Repository Settings and Secrets

In every follower:

- The Actions setting "Allow GitHub Actions to create and approve pull requests" is on.
  It is one checkbox covering both abilities; the sync needs only the first.
- `CLAUDE_CODE_OAUTH_TOKEN` is present, as it already is for the review workflow.
- The ruleset on the default branch stays as it is;
    the sync creates branches and pull requests and never merges.
- Python 3.11 or later and mise are available, as the README states.

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
  Gained: comments in the catalog and the manifest, and standard-library parsing.
  Sacrificed: a follower on an older Python must install one, which mise makes a one-line step.
  JSON would remove the prerequisite and the comments with it; the comments were worth more.
- **File tasks over `mise.toml` entries.**
  Gained: the tasks travel as files and `mise.toml` stays each repository's own.
  Sacrificed: a follower that does not use mise runs the scripts directly, which the README
    shows; nothing else about them needs mise.
- **Regions and divergences, declared by the follower.**
  Gained: files that mix the hub's text with the follower's own can be synced at all,
    and every declaration about a follower lives in its own manifest.
  Sacrificed: a matcher, and above all a regex one, is something a maintainer can write that the
    comparison accepts but a reader cannot verify by eye;
    the proposal shows matched text, and the tests cover both forms.
  Unproven: whether regions stay trackable as both sides edit around them.
  The first convergence milestone tests this on the real mixed files;
    if it fails, those files return to being each repository's own and the README carries their
    baseline as a checklist.
  Not expressible: an instruction such as "keep the broad strokes of every root `mise.toml` in
    sync", which no matcher can state;
    the delivery plan records it as likely to be wanted and deferred until regions and divergences
    have been tried.
- **Decisions in the manifest, not a log.**
  Gained: one file per follower, and dates and authors from history for free.
  Sacrificed: the narrative of a decision is a commit message rather than a log entry,
    and finding it means `git log` on the manifest rather than reading one file.
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
- **A single hub per follower.**
  Gained: one `hub` line, one workflow, and the hub topology the analysis chose.
  Sacrificed: a private repository cannot sync directly with another;
    it reaches it through the hub, which the analysis judged strictly safer.
- **No sync of the hub from a follower.**
  Gained: the hub runs nothing and knows no follower.
  Sacrificed: nothing automated ever writes to the hub;
    every change to it is a pull request a human opened.

## Success Criteria

- `process-sync:test` passes, building its fixture repositories with `git init` at test time
    and covering: two converged repositories (exit `0`, nothing reported);
    an edit, an addition, a removal, a rename, a rename plus edit, and a move,
    each reported with the right status;
    a region adopted with literal matchers and one with regex matchers, identical and differing;
    a `replace` and a `patch` divergence each making a differing file compare identical;
    a renamed entry compared as one; a decline reported as `declined`, and one whose hub file
    changed since its `as_of` noted; a suggestion not adopted reported as `suggested`;
    a matcher matching twice, a patch that does not apply, and a missing source each reported as
    `error` with exit `2`; a dirty working tree reported and excluded;
    and the reference check catching a dangling link, a dangling `@`-import, and a dangling skill
    pointer.
- `process-sync:deliver --dry-run` on a sample output directory prints every branch, pull request,
    question, and approval request it would create and creates nothing; run for real and then
    again, the second run creates nothing and reports what exists.
- `process-sync:deliver` refuses a unit naming a path the manifest does not adopt,
    and carries a workflow file as a patch under `pending/` rather than writing it.
- A unit with an open decision yields one `Sync decision` issue and no pull request;
    recording the decision in the manifest and running again yields the pull request and closes
    the issue.
- This repository and its first follower are converged by the by-hand sequence in the README
    before the workflow exists, and the workflow's first run against the same state creates nothing.
- A pull request created by the unattended run in a follower shows its workflow runs
    parked until a maintainer approves them.
- A full unattended run in a follower against a converged hub creates nothing;
    against a hub with one merged process change, it opens one pull request carrying that change
    within one day.
- The propose job fails before uploading when a file under `out/` contains the OAuth token's
    value, demonstrated on a fixture.
- With the egress block in place, a command run in the agent's job that tries to reach any host
    other than Anthropic's API fails, demonstrated on a fixture; the hosts allowed were found by an
    audit run and are listed in the workflow.
- The agent's tool allowance in the workflow names no tool that accepts a network destination,
    and `process-sync:compare` run with the unattended variable set refuses a counterpart other than
    the manifest's hub, and refuses to clone, with exit `2`.
- `process-sync:publish --dry-run` against an approval whose hash no longer matches the content
    refuses; against a valid approval it shows the exact diff and, after `yes`, opens one pull
    request in the hub whose body names no private repository.
- Neither repository holds any credential for the other, before or after the first milestones:
    the only secrets in a follower are those the review workflow already needs.
- The hub's `.github/workflows/process-sync.yml` runs and creates nothing,
    and the hub's content and history contain no follower's name.
- `process-sync:check-refs` passes in the hub after the `@`-import fix, and fails on a fixture with
    one of the ten root-relative imports restored.
- Enrolling a scratch repository with `process-sync:enroll` and one sync yields one pull request,
    after which the comparison between it and the hub reports every adopted entry identical.

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
    which the exit codes, the matcher rules, and the failure issue follow;
    [Mocks Are Usually Dumb](../engineering-principles/2026-01-15-avoid-mocks.md),
    which is why the tests build real repositories;
    and [YAGNI](../engineering-principles/2026-01-06-yagni.md),
    which is why there is one hub, no App, and no registry.
