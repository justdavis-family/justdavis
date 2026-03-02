# Repo Rename and GitHub Organization Transfer

## Goals

Contributions from family members such as [@webdavis](https://github.com/webdavis)
  are expected,
  and that would be a bit odd if this is explicitly a _personal_ repo
  rather than the family's repo.
The goal is to evaluate whether to:

1. Rename the repository from `karlmdavis` to `justdavis`.
2. Transfer it to a GitHub organization,
     so it's owned by the family rather than a single user.

## Questions and Uncertainties

Before deciding, the following questions needed answers:

1. What are the GitHub organization pricing tiers,
     and what does it cost for 2 users?
2. How do the features of a free org compare
     to a personal Pro account and a Team org?
3. Do personal Pro subscription benefits
     transfer to repos owned by an org?
4. How do GitHub redirects behave
     across a rename followed by an org transfer?
5. Which files in the repo contain personal or single-owner language
     that would need updating?

## Findings

### 1. GitHub Organization Pricing

GitHub offers three organization tiers:

| Tier | Price |
|------|-------|
| Free | $0/month. |
| Team | $4/user/month (billed annually). |
| Enterprise Cloud | $21/user/month (billed annually). |

For 2 users:

| Plan | Monthly Cost | Annual Cost |
|------|-------------|-------------|
| Free | $0. | $0. |
| Team | $8. | $96. |
| Enterprise | $42. | $504. |

### 2. Feature Comparison: Free Org vs. Personal Pro vs. Team Org

| Feature | Pro (personal) | Free org | Team org ($4/user/mo) |
|---------|---------------|----------|----------------------|
| Branch protection rules. | Yes. | Public repos only. | Yes. |
| Required pull request reviewers. | Yes. | Public repos only. | Yes. |
| Multiple PR reviewers. | Yes. | Public repos only. | Yes. |
| Code owners (`CODEOWNERS`). | Yes. | No. | Yes. |
| Team-based PR reviewers. | N/A (no teams). | No. | Yes. |
| Scheduled PR reminders. | No. | No. | Yes. |
| Security overview. | No. | No. | Yes. |
| Draft PRs. | Yes. | Yes. | Yes. |

Additional resource limits:

- **Free org**: 2,000 CI/CD minutes/month, 500 MB Packages storage
    (both unlimited for public repos).
- **Team org**: 3,000 CI/CD minutes/month, 2 GB Packages storage.
- **Enterprise**: 50,000 CI/CD minutes/month, 50 GB Packages storage.

Since this repository is **public**,
  the branch protection and required reviewers limitations on the Free org plan
  do not actually apply
  — those restrictions only affect private repos.
The main features lost by going Free org instead of Team
  are code owners and team-based review,
  which are not needed for a small family project.

### 3. Personal Pro Benefits Do Not Transfer to Org Repos

Personal GitHub Pro benefits (branch protection, required reviewers,
  code owners on private repos, etc.)
  apply **only to repos owned by the personal account**.
If the repo is transferred to an org,
  those features are governed by the **org's plan**,
  not the individual's Pro subscription.
The Pro subscription would still apply
  to any repos remaining under the personal `karlmdavis` account.

As of January 12, 2026,
  GitHub deprecated the ability to convert a personal user account
  directly into an organization.
The current workflow is to create an organization separately
  and use the "Transfer" feature to move repositories into it.

### 4. GitHub Redirect Behavior Across Rename and Transfer

#### Rename Redirects

When you rename a repository,
  GitHub automatically redirects issues, wikis, stars, followers, and web traffic
  to the new name.
All `git clone`, `git fetch`, and `git push` operations
  targeting the old location continue to function
  as if made on the new location.
GitHub recommends updating local clones
  with `git remote set-url origin NEW_URL`.

#### Redirect Chaining

Redirects chain across rename and transfer:

1. **Rename**: `karlmdavis/karlmdavis` → `karlmdavis/justdavis`
     — GitHub creates a redirect from the old name.
2. **Transfer to org**: `karlmdavis/justdavis` → `justdavis/justdavis`
     — GitHub creates another redirect.
3. Both old URLs (`karlmdavis/karlmdavis` and `karlmdavis/justdavis`)
     redirect to the final location.

#### Duration and Caveats

Redirects last **indefinitely**, with one caveat:
  if anyone later creates a new repo at the old name,
  that breaks the redirect.
As long as no one creates a new `karlmdavis/karlmdavis` repo,
  the old links keep working.

**GitHub Actions caveat**:
  if a workflow uses an action from a renamed repository,
  it will produce a "repository not found" error.
GitHub Actions do **not** follow renames.
Workaround: create a new repository and action with the new name
  and archive the old repository.
This caveat does not apply here
  since this repo does not publish reusable GitHub Actions.

#### Sources

- [Renaming a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/renaming-a-repository)
    — GitHub Docs.
- [Transferring a repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository)
    — GitHub Docs.
- [How long does GitHub forward renamed/moved repos?](https://github.com/orgs/community/discussions/22669)
    — GitHub Community.

### 5. Files Containing Personal or Single-Owner Language

The following files reference the personal repo name
  or use first-person/single-owner language that should be updated:

| File | What needs changing |
|------|---------------------|
| `README.md` | Title ("Personal Monorepo for @karlmdavis"), multiple first-person references, "personal open source" (twice). |
| `CONTRIBUTING.md` | First-person language ("I'm so glad... my collection", "letting me know", "for my own reference"). |
| `.claude/CLAUDE.md` | "personal open source monorepo for @karlmdavis". |
| `.claude/rules/pr-workflow.md` | "self-review for solo project". |
| `renovate.json` | `"assignees": ["karlmdavis"]` hardcoded as sole assignee. |

Note: `design/engineering-principles/README.md` uses "personal preferences"
  in a generic instructional sense — that usage is fine as-is.

### 6. Renames and Migration Steps

The following renames are needed as part of the migration:

1. **GitHub repo rename**:
     `karlmdavis/karlmdavis` → `karlmdavis/justdavis`
     (via `gh repo rename justdavis`),
     then later transfer to the `justdavis` org.
2. **Local directory rename**:
     `karlmdavis.git` → `justdavis.git`
     (in `/Users/karl/workspaces/justdavis/`).
3. **VS Code workspace rename**:
     `karlmdavis.code-workspace` → `justdavis.code-workspace`
     (in `/Users/karl/workspaces/justdavis/`),
     and update the `path` inside it
     from `karlmdavis.git` to `justdavis.git`.
4. **Claude Code project directory**:
     `~/.claude/projects/-Users-karl-workspaces-justdavis-karlmdavis-git/`
     — see below.

#### Claude Code Project Directory

Claude Code auto-creates project directories under `~/.claude/projects/`
  based on the working directory path.
Renaming the local directory will cause
  a new project directory to be auto-created on the next launch
  (at `-Users-karl-workspaces-justdavis-justdavis-git/`).
The old directory becomes orphaned and is never cleaned up automatically.

The existing project directory contains only session transcript `.jsonl` files
  — no memory directory (`MEMORY.md` or topic files) exists.
There is nothing to migrate;
  the old orphaned directory can be deleted at the user's convenience.

**Important**: the Claude Code project directory rename
  should be done after the active session ends,
  as renaming during an active session would be problematic.

## Summary

### Questions Answered

All five questions from above have been answered:

1. Free org is $0; Team is $8/month for 2 users.
2. Free org loses code owners and team-based review vs. Pro,
     but branch protection and required reviewers work fine on public repos.
3. Pro benefits do not transfer to org repos
     — but this doesn't matter for a public repo on a Free org.
4. Redirects chain across rename + transfer and last indefinitely
     (unless someone creates a repo at the old name).
5. Five files need text updates; see the table above.

### Decision

Move to a **free GitHub organization** named `justdavis`.
This makes the most sense
  for a shared family repo where contributions from family members are expected,
  and the free tier provides everything needed for a public repository.

### Open Items

- The actual rename, org creation, transfer, file edits,
    and local renames are tracked separately as implementation work.
