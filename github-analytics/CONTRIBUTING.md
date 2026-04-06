# Contributing to GitHub Analytics Collector

See the [repository-level CONTRIBUTING.md](../CONTRIBUTING.md)
  for the general development workflow, PR process, and conventions
  that apply to all projects in this monorepo.
This file covers setup steps specific to this project.

## Project-Specific Setup

### 1. Install mise

This project uses [mise](https://mise.jdx.dev/) for tool and task management.
Follow the [getting started guide](https://mise.jdx.dev/getting-started.html)
  to install it if you haven't already.

### 2. Set Up Credentials (`.env`)

Traffic and repository metadata endpoints require a GitHub token with `repo` scope.
Copy the sample and fill it in:

```bash
cp sample.env .env
# Edit .env and set GITHUB_TOKEN to a Classic PAT with repo scope
```

The `.env` file is gitignored and will be copied automatically into new worktrees
  via `.worktreeinclude`.

### 3. Run the Test Suite

```bash
cd github-analytics
MISE_EXPERIMENTAL=1 mise run ':ci'
```

This runs unit tests (VCR cassettes — no live HTTP), linting, and type checking.
The smoke test (see below) is also included in `:ci` but skips automatically
  if its prerequisites are not met.

### 4. Set Up the Smoke Test Config (`config.smoke.yaml`)

The smoke test runs the full collect-and-report pipeline against the live GitHub API.
Copy the sample and add a small set of repositories you have push access to:

```bash
cp config.smoke.sample.yaml config.smoke.yaml
# Edit config.smoke.yaml and add 4–8 repos you own
```

`config.smoke.yaml` is gitignored and will be copied into new worktrees automatically.
Run the smoke test with:

```bash
MISE_EXPERIMENTAL=1 mise run ':test:smoke'
```

### 5. Recording New VCR Cassettes

Unit tests replay recorded HTTP interactions stored in `tests/cassettes/`.
If you add a new test or change an API call, re-record the cassette:

```bash
# Requires GITHUB_TOKEN in .env (live HTTP)
MISE_EXPERIMENTAL=1 mise run ':test' -- --record-mode=new_episodes -k test_name_here
```

Commit the updated cassette alongside your code change.
