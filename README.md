# Monorepo for [@justdavis-family](https://github.com/justdavis-family/)

Welcome to this collection
  of small projects, home lab tooling, and other assorted experiments and resources.
This is all open sourced in the hope of sharing knowledge
  — and on the off-chance that others can directly use some of it.
If you _do_ find something here particularly enlightening or useful,
  please consider giving the repository a **star** on GitHub
  and letting us know about it over in the
  [discussions](https://github.com/justdavis-family/justdavis/discussions) section.

## What's In Here?

| Project | Description |
|---|---|
| [github-analytics](github-analytics/README.md) | Collects and stores GitHub repository analytics data that the API exposes but the web UI doesn't retain historically. |

## How is this Repository Organized?

This repository is roughly organized by domain,
  with different subtrees for the different types of projects.

```
.github/          GitHub workflows and other config.
.claude/          Agent instructions and other config.
design/           Design documents, workflow, and related materials.
github-analytics/ GitHub analytics collector and reporter.
mise.toml         mise-en-place: dev env, tools, and tasks.
```

### Why a Monorepo?

Monorepos are an unusual/unexpected choice for personal open source,
  but the friction of having to spin up a new repository and all the attendant infrastructure
  (build tooling, agent instructions, CI/CD, etc.)
  every time we want to create a new little widget or whatnot was too high
  — and so now we stick anything new in here.
Most of this open source work is shared less because folks might want to _use_ it,
  but more because folks might want to _reference_ it.
For instance, we doubt anyone cares to configure their home lab
  with exactly the same services and configuration as ours,
  but it's entirely possible that someone is trying to get Kerberos and OpenLDAP working together
  and can reference the Ansible roles for that combo.

## How Do I Develop In and Contribute To This Repository?

See the [CONTRIBUTING.md](CONTRIBUTING.md) file
  for development environment setup and contribution guidelines.

## What License Is This Being Distributed Under?

This repository is licensed under the MIT License.
See the [LICENSE](LICENSE) file for details.
