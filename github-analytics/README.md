# GitHub Analytics Collector

Collects GitHub repository analytics data that the GitHub API exposes
  but the web UI does not retain historically —
  things like daily traffic views, clone counts, and referrer breakdowns —
  and stores them in a separate data repository.
A companion reporter generates Markdown README files with tables and charts
  in the same companion data repository
  so the data is easy to browse on GitHub.

## How It Works

A GitHub Actions workflow runs once daily and does three things:

1. **Collect** — calls the GitHub API for each configured repository,
   fetching traffic views, clone counts, top referrers, top paths,
   star events, fork events, release download counts, repository metadata,
   and workflow run summaries.
   Results are written to per-metric NDJSON files in a separate data repository.
   Snapshot metrics (e.g. today's view count) use upsert semantics
   so later runs in the same day replace earlier partial values.

2. **Report** — reads the NDJSON files and generates Markdown README files
   at three levels: one for the entire data repository, one per GitHub owner,
   and one per repository.
   Each per-repo README includes traffic tables, current star and fork counts,
   and release download counts.

3. **Commit and push** — commits any new or updated files to the data repository.

Traffic data is only available for repositories you have push access to,
  so the token requires `repo` scope.

## Deploying Your Own Instance

### Prerequisites

- A GitHub account or organization owning the repositories you want to track.
- A separate GitHub repository to store the collected data
  (e.g. `your-org/github-analytics-data`).
  It can be public or private.
- A Classic GitHub Personal Access Token (PAT) with `repo` scope
  (see [Create a Personal Access Token](#create-a-personal-access-token) below).

### Create a Personal Access Token

The collector needs a Classic PAT with `repo` scope to read traffic data —
  GitHub's traffic API requires push access to the source repository.
The same token type is needed for the smoke test during local development.

To create one:

1. Go to **GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)**.
2. Click **Generate new token (classic)**.
3. Set the **Note** to something descriptive (e.g. `ANALYTICS_DATA_PAT`).
4. Select the **`repo`** scope (the top-level checkbox — this grants full repo access).
5. Set an appropriate expiration (90 days is a reasonable default; you'll need to rotate it).
6. Click **Generate token** and copy the value immediately — GitHub only shows it once.

For a production deployment, store the token as a repository secret named `ANALYTICS_DATA_PAT`
  under **Settings → Secrets and variables → Actions → New repository secret**.
For local development and the smoke test, store it in `github-analytics/.env`
  (see [CONTRIBUTING.md](CONTRIBUTING.md) for setup instructions).

### Setup

1. **Create the data repository** — create an empty repository to hold the
   collected NDJSON files and generated READMEs.

2. **Add the PAT as a secret** — create a PAT per the section above, then add it
   as a repository secret named `ANALYTICS_DATA_PAT`.

3. **Update the workflow** — open `.github/workflows/github-analytics.yml` and:
   - Set the `repository` field under "Checkout data repo" to your data repository name.
   - Edit the "Write collector config" step to list the repositories you want to track.
     Supported patterns:

     ```yaml
     repos:
       - owner/repo-name       # a specific repository
       - org:your-org          # all repos in a GitHub org
       - user:your-username    # all repos for a GitHub user
     ```

   The repository list lives in the workflow rather than a checked-in config file
     so that each fork or deployment maintains its own list without risk of merge conflicts.

4. **Trigger the workflow** — navigate to
   **Actions → Collect GitHub Analytics → Run workflow**
   to run the first collection manually and verify everything is working.
   After that, the workflow runs automatically every day at 6 AM UTC.

## Contributing / Local Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for local setup instructions,
  including how to configure credentials, run tests, and run the smoke test.
