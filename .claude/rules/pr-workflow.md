# PR Workflow

This repository uses a **PR-based workflow** with branch protection rules enforced on main.

## Core Principles

- **ALL changes** must go through pull requests — direct commits to main are blocked.
- **ALWAYS** create a feature branch before making any code changes.
- **NEVER** attempt to commit directly to the main branch.

## Change Types

One vocabulary, taken from [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/),
  runs through the whole life of a change:
  the branch it is developed on, the commit that lands it, and the label on its PR.
Keeping the three identical means the branch name predicts the commit subject,
  and neither can quietly disagree with the label.

| Type | Branch | Commit / PR title | PR label | Use for |
|---|---|---|---|---|
| `feat` | `feat/<name>` | `feat: …` | `feat` | New features or capabilities. |
| `fix` | `fix/<name>` | `fix: …` | `fix` | Bug fixes. |
| `docs` | `docs/<name>` | `docs: …` | `docs` | Documentation and design-process changes. |
| `chore` | `chore/<name>` | `chore: …` | `chore` | Dependency updates, tooling, and other maintenance. |
| `ci` | `ci/<name>` | `ci: …` | `ci` | CI workflow and automation changes. |
| `refactor` | `refactor/<name>` | `refactor: …` | `refactor` | Restructuring without behavior change. |

Only `feat` and `fix` are mandated by the Conventional Commits spec itself;
  the other four come from the Angular convention that the spec references.
This list is deliberately short — resist adding types until one is genuinely needed.

Scoped prefixes are allowed where a change is confined to one project
  (`docs(squawkbox): …`), as is the `!` breaking-change marker (`feat!: …`).
Scopes are especially worth using here because this is a monorepo:
  `git log --oneline` spans every project at once,
  so the scope is often the fastest way to tell whose history you are reading.
Note that a scope can only be expressed in the commit and PR title —
  branch names and labels carry the bare type,
  since a scoped variant of each would multiply the vocabulary for no gain.

**The PR label duplicates the title prefix on purpose.**
It makes the vocabulary visible to anyone reading a PR list,
  and `label:docs` is a cleaner filter than searching title text.
That duplication is only worth its cost once it is applied automatically,
  which is tracked in
  [#34](https://github.com/justdavis-family/justdavis/issues/34);
  until that lands, treat the label as best-effort rather than expected,
  and never let it contradict the title.

## Workflow Using gh CLI

1. Create and checkout a branch, prefixed per the table above:
     `git checkout -b feat/your-feature-name`.
2. Make changes and commit to the branch.
3. Push branch: `git push -u origin feat/your-feature-name`.
4. Create PR: `gh pr create --title "Title" --body "Description"`.
   Title it with the same type prefix as the branch, assign it to yourself,
     and apply the matching type label
     — see [`github-issues.md`](github-issues.md) for what else does and doesn't get set.
5. Review and approve PR (self-review is acceptable, particularly for small changes).
6. Merge the PR — squash by default; see [Merging PRs](#merging-prs) below
     for the commit-message convention and exact `gh` invocation.
7. Branches are automatically deleted after merge (GitHub setting).

## Merging PRs

Default to **squash merges** to keep `main`'s history linear and easy to scan.
The squashed commit lives in `git log` forever, so invest in writing a good message.

### Commit Message

- **Subject**: `<type>: <description> (#<PR-number>)`,
    where `<type>` is from the [Change Types](#change-types) table above.
  GitHub does not append `(#<PR-number>)` automatically when `--subject` is supplied,
    so include it manually for traceability back to the PR.
- **Body**: copy the **Summary** and **Context** sections of the PR description verbatim,
    separated by a blank line.
  These two sections explain _what_ changed and _why_,
    and are the most useful parts for a future reader of `git log` or `git blame`.
  Drop the `## Summary` / `## Context` headers if the prose reads naturally without them.

### Command

Pass `--subject` and `--body` explicitly
  so the merge commit is composed deliberately
  rather than inheriting the entire PR description (success-criteria checklist included):

```bash
gh pr merge <PR#> --squash --delete-branch \
  --subject "<type>: <description> (#<PR#>)" \
  --body "$(cat <<'EOF'
<Summary section text>

<Context section text>
EOF
)"
```

`--delete-branch` removes the remote branch after merging
  and switches the local checkout back to `main`,
  also deleting the merged local branch.

### Other Merge Strategies

- `--merge` (true merge commit) is acceptable
    when preserving individual commits has value
    — e.g. a series of independent commits that each stand on their own
    and are worth keeping in history separately.
- `--rebase` is generally avoided in this repo.

### Bypassing Review

Use `--admin` only when bypassing review has been explicitly authorized
  (e.g. trivial changes the author has confirmed, or hotfixes).

## PR Requirements

### Description Outline

Every PR description needs these sections:
  **Summary**, **Design Process**, **Success Criteria**, **Test Plan**, and **Context** —
  plus **Acceptance Criteria** when the PR delivers a delivery-plan milestone.

[`.github/PULL_REQUEST_TEMPLATE.md`](/.github/PULL_REQUEST_TEMPLATE.md) pre-fills all of them,
  along with guidance on what belongs in each,
  so a new PR starts with the outline already in place and there is nothing to copy by hand.

### Description Formatting

GitHub PR and issue descriptions and comments support GitHub Flavored Markdown,
  with one important difference:
  all line breaks are preserved.
Accordingly, our usual line-wrapping and continuation formatting rules should not be applied
  to PR or issue descriptions or comments.

### Success Criteria

**Every pull request must include a "Success Criteria" section** in the PR description.

The criteria required of *all* PRs are pre-filled by
  [`.github/PULL_REQUEST_TEMPLATE.md`](/.github/PULL_REQUEST_TEMPLATE.md);
  don't delete them, and don't tick one until it is actually true.

#### Task-Specific Criteria

On top of those, add the criteria for the kind of change being made.
These are not in the template — carrying all four sets in every PR would bury the relevant one.

**For refactoring PRs:**

- [ ] No functionality changes (existing tests still pass without modification).
- [ ] Test coverage maintained or improved.
- [ ] Performance benchmarks maintained or improved.

**For new feature PRs:**

- [ ] Feature documentation added to relevant docs.
- [ ] Tests added for main user workflows.

**For bug fix PRs:**

- [ ] Test added that reproduces the bug (fails before fix, passes after).
- [ ] Root cause documented in PR description or commit message.
- [ ] Related bugs checked for similar issues.

**For documentation PRs:**

- [ ] Markdown formatting follows project guidelines.
- [ ] All links verified working.
- [ ] Spelling and grammar checked.
