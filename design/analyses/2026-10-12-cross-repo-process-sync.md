# Keeping the Development Process in Sync across Repositories

## Question

The [vision](../product-vision/2026-09-04-design-process-sync.md) and its requirements say what a
  cross-repository sync of this monorepo's development process must achieve,
  and deliberately leave open how.
Two families of mechanism were on the table from the start:
  refactor the process into one or more shared agent skills, so that it is shared intrinsically;
  or keep it as files in each repository and replicate changes between them.
Both families then raise the same operational questions,
  and the vision's "Compromise Stays Contained" metrics make the answers security questions.

This analysis settles, with evidence:

1. Where the process definition should live:
     in a shared skill or plugin, in each repository, or some of each.
2. What an unattended sync run in a following repository can do on its own,
     with what credential, and whether it needs an agent.
3. How a change that a human has approved for publication crosses from a private repository to a
     public one without either repository holding a credential that an attacker could use to
     compromise the other, and without anything forwarded running before a human chooses.
4. What the two repositories' branch rules enforce today, and what that changes.
5. What topology serves N repositories, not two.
6. Which parts of the process content no automation may carry.

Findings are labeled by provenance:
  *verified in docs* (the cited page says it), *verified locally* (checked on 2026-10-12 against the
  two repositories, by read-only API calls and one-shot `claude -p` sessions),
  or *inferred* (follows from verified facts but no page states it).
The private repository that follows the process is never named.

## Findings

### 1. A Skill or Plugin Cannot Carry Most of the Process

The process content is five kinds of thing:
  the `design/` READMEs and templates; the `design-process` skill;
  the agent rules under `.claude/rules/`; the `design/*/CLAUDE.md` stubs;
  and the pull-request template, issue templates, and workflows under `.github/`.
The repository-wide brief at `.claude/CLAUDE.md` is local by design, as the vision says,
  because it describes the repository it sits in;
  a general paragraph inside it can still be adopted on its own, which the engineering design covers.

A Claude Code plugin can ship skills, agents, commands, hooks, MCP and LSP servers, workflows,
  output styles, themes, and executables.
It cannot ship a `CLAUDE.md` — the validator warns when it finds one at the plugin root —
  and it cannot ship `.claude/rules/` files, which load only from the project's and the user's own
  `.claude/rules/` directories, never from a plugin
  ([plugin components](https://code.claude.com/docs/en/plugins/components.md),
  [memory](https://code.claude.com/docs/en/memory.md)).
Nothing GitHub consumes from `.github/` can come from a plugin either.
*Verified in docs.*

Mods do not change this.
A mod is a plugin made of JavaScript or TypeScript event handlers that Claude Code calls in its own
  process when a tool is called, a prompt is submitted, or part of the interface is drawn
  ([mods](https://code.claude.com/docs/en/plugins/mods/overview.md)).
It changes how Claude Code behaves at runtime; it places no file in the repository,
  and the same manifest rules apply to the plugin that carries it.
A mod could in principle inject process instructions into every session by handler,
  but that would take the process out of the repository and out of human sight entirely,
  which is the trade-off the vision already decides against.
*Verified in docs; the last sentence is inferred.*

So under the shared-skill family, only the skill and the documents it carries as supporting files
  (the READMEs and templates could be reworked into that) would be shared intrinsically.
The rules, the stubs, and everything under `.github/` would still have to be replicated.
The family is not an alternative to replication; it is replication plus a second mechanism,
  with the process definition split across the two.
*Inferred.*

It would also move the human-facing documents out of the repository.
`CONTRIBUTING.md` and `.claude/CLAUDE.md` would point at a plugin's source repository,
  reversing the direction of recent changes here, #38 above all,
  which made the in-repository contributor documents the single statement of the conventions
  because humans read those and do not reliably read `.claude/`.
The vision names this trade-off and leaves it to this analysis;
  the finding above decides it, since the family cannot deliver its one advantage
  — a single home — anyway.
*Inferred.*

### 2. The Repository's `@`-Imports Have Never Worked

`@` paths in memory files resolve relative to the importing file, not the project root
  ([memory](https://code.claude.com/docs/en/memory.md), "Import additional files").
Every `@`-import in this repository is written root-relative:
  `@CONTRIBUTING.md` in `.claude/CLAUDE.md`, `@design/README.md` in the design-process rule,
  `@design/<type>/README.md` in each `design/<type>/CLAUDE.md` stub,
  and `@design/engineering-principles/` in the engineering-principles rule,
  which names a directory and so imports nothing in any form.
Each of the others resolves to a path that does not exist, and imports nothing.
*Verified in docs.*

One-shot sessions in this worktree confirm it:
  a phrase from `.claude/CLAUDE.md` and one from a rules file are reported as loaded;
  a phrase from `CONTRIBUTING.md` and one from `design/README.md` are not.
A scratch project with both path forms shows the file-relative form loads, in rules files too.
*Verified locally.*
The defect is tracked as [#44](https://github.com/justdavis-family/justdavis/issues/44).

For this analysis the consequence is that the loading model constrains the design less than the
  requirements assumed.
What an agent has at launch is `.claude/CLAUDE.md`, the rules (path-scoped ones on demand),
  and the skills' descriptions.
It reaches the READMEs and templates only by following a link or invoking the skill.
That favors keeping those documents where links already point — in the repository —
  and keeping the skill thin, as it is.
*Inferred.*

### 3. Third-Party File-Sync Actions Fail the Containment Metric

The hosted "sync files between repositories" actions require a personal access token with the
  full `repo` scope, or a GitHub App token, held in the sending repository;
  the automatic `GITHUB_TOKEN` cannot reach another repository
  ([repo-file-sync-action](https://github.com/BetaHuhn/repo-file-sync-action),
  [files-sync-action](https://github.com/adrianjost/files-sync-action)).
Their deletion handling is opt-in or on by default, and neither documents renames,
  so a renamed file arrives as a deletion plus an addition.
*Verified in their READMEs; the rename behavior is inferred from their silence.*

They also know nothing of a declaration of what is adopted, of declared divergences,
  or of recorded decisions,
  which [Propose a Process Sync](../product-requirements/2026-09-06-process-sync-proposal.md)
  requires.
The requirements already settled that the comparison, grouping, and proposal are the sync skill's
  job; what remains for the mechanism is only how the skill is run unattended
  and how its output lands.
`git subtree` and `git merge` from a dedicated process repository were considered for the same
  slot and rejected on a simpler ground:
  the two repositories' histories are unrelated (this one begins in March 2026, the other in
  October 2025), so any merge would import an entire tree, and the public monorepo would become a
  spoke of a third repository that exists only to hold the process.
*Verified locally; the topology point is inferred.*

A template repository is not a mechanism for this problem at all:
  it copies files once, when a repository is created, and has no notion of a later change.
It could serve only the enrollment of a brand-new repository,
  and the enrolling pull request already does that.
*Inferred.*

### 4. An Unattended Run Needs No Credential beyond Its Own Repository's

The direction that matters most — a private repository following the public one — needs nothing
  from the public side.
Checking out a public repository from another repository's workflow needs no token
  ([actions/checkout](https://github.com/actions/checkout#checkout-multiple-repos-private)).
Creating pull requests and issues in the workflow's own repository needs only `GITHUB_TOKEN`
  with `contents: write`, `pull-requests: write`, and `issues: write`,
  plus the repository setting "Allow GitHub Actions to create and approve pull requests",
  which is off by default on personal-account repositories
  ([managing Actions settings](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/enabling-features-for-your-repository/managing-github-actions-settings-for-a-repository)).
*Verified in docs.*

Both repositories currently default `GITHUB_TOKEN` to read-only and forbid it from approving
  pull requests, so the workflow must request those permissions explicitly and the setting must be
  turned on in the following repository.
*Verified locally.*

The "approve" in that setting's name means submitting an approving pull request *review* with
  `GITHUB_TOKEN`; it has nothing to do with approving parked workflow runs, which stays with a human
  who has write access.
The sync needs only the "create" half, but the setting is one checkbox,
  so a following repository that turns it on also lets its own workflows approve pull requests.
In the private repository that changes nothing, since its ruleset requires no approvals;
  in the public repository the question never arises, since no sync workflow runs there.
*Verified in docs for the setting's scope; the consequence is inferred.*

The comparison and the reference check need no agent.
The proposal does: classifying differences from history, grouping them, and writing descriptions
  is what the skill is for.
Running it unattended means running Claude Code in the workflow,
  which this repository already does for review through `claude-code-action`,
  authenticated by the Claude app's OAuth token rather than a repository credential.
That credential's blast radius is spend and whatever the agent can do with the workflow's own
  `GITHUB_TOKEN`, which reaches only the repository it runs in.
*Inferred from the existing review workflow and the token facts above.*

Private plugin marketplaces are cloned with the git credentials already on the machine;
  whether `claude-code-action`'s `plugin_marketplaces` input does the same is not stated
  ([installing plugins](https://code.claude.com/docs/en/plugins/install.md)).
It does not matter here: the sync skill is process content and arrives in each repository the same
  way the design-process skill does, so nothing needs installing from anywhere.
*Verified in docs; the last sentence is a design choice this analysis recommends.*

### 5. `GITHUB_TOKEN`-Created Pull Requests Get the Containment Metric for Free

When a workflow creates or updates a pull request using `GITHUB_TOKEN`, the resulting
  `pull_request` runs are created in an approval-required state and do not run until a user with
  write access approves them; a `GITHUB_TOKEN` push triggers no `push` workflow at all.
A pull request created with a personal access token or an App token triggers workflows
  immediately
  ([triggering a workflow from a workflow](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow#triggering-a-workflow-from-a-workflow)).
*Verified in docs.*

This is exactly the vision's second containment outcome,
  "nothing forwarded executes until a human has reviewed it and chosen to run it",
  enforced by GitHub rather than by convention.
It also means the obvious "improvement" — using a stronger token so the inbound pull request's
  checks run automatically — would remove the property.
Inbound pull requests must be created with `GITHUB_TOKEN`, on purpose.
*Inferred.*

A human applying a label afterwards is an event the human triggered,
  so the label-gated review workflow runs for a bot-opened pull request once a maintainer labels it.
*Inferred from the actor-based rule on the same page.*

No setting makes same-repository branch pull requests wait for approval in general;
  the fork-approval settings apply to forks of public repositories,
  and GitHub reports that fork approval "is not allowed for private repositories".
The `GITHUB_TOKEN` behavior above is the only such gate that exists.
*Verified in docs and locally.*

### 6. Outbound Publication: By Hand Is Safe; a Token as the Maintainer Is Not

[Publish Approved Outbound Changes](../product-requirements/2026-10-04-publish-outbound-changes.md)
  requires that a maintainer can always publish by hand, and that no repository is *required* to
  hold a credential an attacker could use to compromise another.
Publishing by hand — the maintainer, in a checkout of the public repository, applying the approved
  unit with their own `gh` authorization after reading the exact content — stores no credential
  anywhere.
It arrives under the maintainer's own account, which the requirement's privacy criterion permits:
  that account is already public as the public repository's maintainer,
  and it says nothing about which private repositories the same person holds.
Every other criterion it meets directly.
Outbound changes have been rare: four items in the five months the
  [divergence inventory](2026-09-04-process-divergence-inventory.md) covers.
*The volume is the inventory's; the rest follows from the requirement.*

The cost is to the vision's equal-effort and bounded-time metrics in the outbound direction,
  which now rest on a maintainer acting rather than on a schedule.
The approval request of the unattended run stays open until its unit is published,
  so a lapse is visible in the private repository rather than remembered;
  past a few items a quarter, the App shape below is the remedy.
*Inferred.*

An automated publisher would need a credential in the private repository that can write to the
  public one.
The two repositories have different owners, an organization and a personal account.
A fine-grained personal access token is limited to one owner, so the public repository's owner
  would need its own token; a GitHub App needs an installation per owner
  ([fine-grained tokens](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens),
  [installing an App](https://docs.github.com/en/apps/using-github-apps/installing-your-own-github-app)).
*Verified in docs.*

The two are not equivalent, because of who the token acts as.
The public repository's ruleset requires a pull request with one approving review on `main`,
  but grants organization admins and the repository's admin role an *always* bypass,
  and the maintainer holds both.
A personal access token acts as the maintainer, so an attacker holding it could push to `main`
  directly, bypassing the ruleset.
A GitHub App acts as itself, holds no bypass unless granted one, and can be minted a token limited
  to one repository and a chosen subset of permissions
  ([rulesets](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-rulesets/creating-rulesets-for-a-repository),
  [App tokens in Actions](https://docs.github.com/en/apps/creating-github-apps/authenticating-with-a-github-app/making-authenticated-api-requests-with-a-github-app-in-a-github-actions-workflow)).
*Verified locally for the bypass; verified in docs for the rest.*

Even an App token that can open pull requests weakens finding 5:
  pull requests it opens run their workflows immediately, so a compromised private repository
  could execute code in the public repository's CI.
The narrowest automated design that keeps containment is therefore:
  an App installed on the public repository only, granted `contents: write` and nothing else,
  pushing a branch under a pattern that a ruleset reserves to it, and never opening the pull
  request — a human opens it, which is the human choosing to run.
Pushing changes under `.github/workflows/` additionally needs the `workflows` permission,
  which the App would not have, so workflow files cannot cross this way;
  see finding 8.
*Inferred from the verified facts above.*

### 7. The Private Repository's Ruleset Enforces Less Than the Requirements Assume

The private repository's ruleset on `main` requires a pull request and thread resolution,
  but zero approving reviews, with no bypass actors.
Whoever opens a pull request there can merge it.
"Reviewed as real content" in that repository is a convention the maintainer keeps,
  not a gate GitHub enforces; with a single maintainer who cannot approve their own pull request,
  requiring an approval would block the workflow rather than protect it.
*Verified locally.*

Two things follow.
The inbound path's safety rests on finding 5, not on review enforcement:
  the pull request exists, its checks are parked, and nothing runs until the maintainer acts.
And the public repository's admin bypass, harmless today, becomes the single most dangerous setting
  the moment any credential acting as the maintainer is stored anywhere;
  "for pull requests only" is the bypass mode that keeps admin convenience without that exposure.
*Inferred.*

### 8. Workflow Files Cross as Patches, Applied by a Human, in Both Directions

Creating or updating files under `.github/workflows/` requires the `workflow` scope on a classic
  token, or the `workflows` permission on a fine-grained token or an App;
  `GITHUB_TOKEN` does not have it, and a push without it is rejected
  ([OAuth scopes](https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/scopes-for-oauth-apps#available-scopes),
  [App permissions](https://docs.github.com/en/apps/creating-github-apps/registering-a-github-app/choosing-permissions-for-a-github-app)).
*Verified in docs; the exact rejection text is community-attested.*

That permission is the whole of the protection; GitHub does not hold back a changed workflow once
  it is on a branch.
A `pull_request` run executes in the context of the pull request's merge commit,
  so it uses the branch's version of every workflow file, including one the pull request changes.
`pull_request_target`, `schedule`, `workflow_dispatch`, `workflow_run`, and the issue, comment,
  and repository-level events use the default branch's copy instead
  ([events that trigger workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows)).
The gates that do exist are the two in finding 5: approval for runs from public forks,
  and the parked runs of a `GITHUB_TOKEN`-created pull request.
A changed workflow on a same-repository branch that a human pushed simply runs.
*Verified in docs.*

So an unattended inbound pull request created with `GITHUB_TOKEN` cannot contain a change to a
  workflow file, and the outbound App of finding 6 must not be granted the permission that would
  let it.
The restriction is by path, though: a file anywhere outside `.github/workflows/` is pushed freely,
  whatever it contains.
A proposal can therefore carry a workflow change as a patch file, committed on the pull request's
  branch outside that directory, with the pull request saying that the patch is to be applied by hand.
The maintainer reviews the patch as text, applies it to the branch, deletes the patch file,
  and pushes with their own authorization.
That push is a human's act, so the changed workflow then runs on the pull request
  as any human-authored change would, which is the containment outcome exactly.
The unit stays whole, in one pull request and in history, and the manual step is one command
  rather than a transcription.
*Inferred.*

The step is still worth keeping manual: it is the one place the sync could otherwise forward
  executable configuration, and the review workflow's prompt is the file the divergence inventory
  found had drifted between the repositories.
*Inferred.*

### 9. The Topology Is a Hub, and the Hub Runs Nothing

Every following repository pulls from the public one and pushes nothing to it unattended.
The public repository holds no sync workflow, no credential, and no list of followers;
  it learns of a follower only when a maintainer publishes an outbound change from it.
A third repository joins by running the same workflow against the same hub,
  with no change anywhere else, which is what
  [Enroll a New Repository](../product-requirements/2026-10-12-enrolling-a-repository.md) requires.
*Inferred from findings 4 to 6.*

Two private repositories sync with each other only through the hub:
  a change made in one reaches the public repository by the outbound path, reviewed there,
  and reaches the other by its own inbound run.
That is slower than a direct link and strictly safer, since every crossing passes a human review
  in the public repository, and it needs no credential between private repositories at all.
A mesh would need a credential per pair and would multiply the finding-6 problem by the number of
  pairs.
*Inferred.*

## Recommendation

1. **The process stays in each repository as files, replicated.**
   The shared-skill family cannot carry the rules, the agent briefs, or anything under `.github/`,
     so it would split the definition across two mechanisms and move the human-facing documents out
     of the repository for no gain.
   The `design-process` skill and the sync skill are process content like any other file,
     replicated by the sync itself; nothing is installed from a marketplace.
   Revisit if plugins gain the ability to ship rules or memory files;
     mods, which are runtime handlers rather than files, do not provide it.
2. **The sync skill is the mechanism; nothing third-party sits between the repositories.**
   On demand, a maintainer runs it locally.
   Unattended, each following repository runs it in its own scheduled and manually dispatchable
     workflow through `claude-code-action`, authenticated as the existing review workflow is,
     with `GITHUB_TOKEN` requesting `contents: write`, `pull-requests: write`, and `issues: write`,
     and the repository setting that allows Actions to create pull requests turned on.
   The deterministic comparison runs first and the agent is invoked only when it reports
     differences, which bounds the spend.
3. **Inbound pull requests are created with `GITHUB_TOKEN`, deliberately.**
   Their workflow runs park until a human approves them, which is the containment metric
     enforced by GitHub.
   No stronger token is ever used for the inbound direction.
4. **Outbound publication is by hand.**
   After approving the request in the private repository, the maintainer applies the unit from a
     checkout of the public repository with their own authorization.
   No cross-repository credential is stored anywhere in the first delivery.
   If outbound volume ever justifies automation, the only acceptable shape is a GitHub App
     — never a personal access token, because the maintainer's admin bypass makes one a key to
     `main` — installed on the public repository alone, granted `contents: write` only,
     pushing to a branch pattern a ruleset reserves to it, with a human opening the pull request.
5. **Workflow files cross as patch files and are applied by a human, in both directions.**
   A proposal carries a change under `.github/workflows/` as a patch committed outside that
     directory; the maintainer reviews it, applies it to the branch, and pushes it themselves.
   No token the sync uses ever holds the `workflows` permission.
6. **The topology is a hub.**
   Followers pull from the public repository; the hub runs nothing and knows no follower;
     private repositories reach each other through it.
7. **Two maintenance items precede the first implementation milestone:**
     fix the `@`-imports ([#44](https://github.com/justdavis-family/justdavis/issues/44)),
     and change the public repository's admin bypass from "always" to "for pull requests only".

Deferred to the engineering design:
  the format and location of what the hub offers and of each follower's declaration of what it
  adopts, how its copies differ, and what it has decided;
  the form of an approval request and how an approval is recorded on it;
  the comparison and reference-check implementation as `mise` tasks;
  the workflow definition, schedule, and how the agent is invoked within it;
  and the test strategy for the skill.
The canonical names and dates for the eight shared engineering principles are not a design
  choice but a sync decision, made by a human at convergence and recorded with that repository's
  other sync decisions,
  as the divergence inventory and
  [Remember Sync Decisions](../product-requirements/2026-09-08-sync-decisions.md) already say.

Revisit this analysis if a repository that is not a monorepo enrolls,
  if plugins gain rules or memory support, if outbound volume grows past a few items a quarter,
  or if GitHub adds a way to restrict who may open pull requests or to gate same-repository
  pull-request workflows behind approval.
