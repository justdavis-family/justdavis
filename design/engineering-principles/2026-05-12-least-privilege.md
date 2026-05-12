# Least Privilege

## Principle

Grant every component the narrowest capability surface that does its job, and no more —
  and treat this as especially load-bearing when the actor on the other side of an interface is
  untrusted or only semi-trusted, such as an LLM/agent with internet access, arbitrary tool use,
  plugins, and prompt-injection exposure.
Prefer fixed-schema, single-purpose operations over general-purpose ones.
When a component needs a powerful permission (filesystem access, OS privacy grants, network reach),
  put it behind a small, stable-identity broker so the powerful permission attaches to the broker,
  not to every consumer that wants the result.

## Rationale

- A smaller capability surface means a smaller blast radius when a consumer is compromised,
    buggy, or manipulated.
- Agents are a worst case: they execute attacker-influenced text, call arbitrary tools, and run from
    churning identities — so any broad permission handed to an agent is both dangerous and fragile.
- Brokering privileged access keeps OS permission grants (e.g. macOS TCC / Full Disk Access)
    confined to a small, audited binary with a stable identity, instead of sprawling onto ephemeral or
    rebuilt executables.
- Narrow, fixed-schema APIs are easier to audit, test, reason about, and keep stable over time.

## Examples

**Good (least-privilege-compliant):**

- A helper that exposes exactly one operation — `get_focus() -> FocusState` — and nothing else.
- A service that reads one specific config file, rather than one that accepts an arbitrary path.
- Putting Full Disk Access on a small, stable, code-signed helper that returns a fixed answer,
    rather than on the agent that wants the answer.
- Issuing a token scoped to exactly the resources and actions needed, with a short lifetime.

**Bad (least-privilege violations):**

- Granting Full Disk Access (or broad Automation/Accessibility permissions) directly to an agent process.
- A "helper" that proxies `read_file(path)`, `run_shell(command)`, `run_shortcut(name)`,
    or `run_osascript(script)` — that is a general-purpose capability, not a narrow one.
- Adding a general "run arbitrary query" endpoint when callers only ever need a handful of fixed answers.
- Reusing one broadly-scoped credential everywhere because minting narrower ones is mildly inconvenient.

## When to Break This Rule

- Genuine general-purpose tools whose entire point is breadth — a shell, a debugger, an admin console —
    used by trusted operators who understand the power they hold.
- Early prototypes where the only consumer is fully trusted first-party code and the cost of narrowing
    later is low — but revisit this before any untrusted or third-party actor (especially an agent)
    is introduced.

## Relationship to Other Principles

- Complements **YAGNI** — don't expose capabilities no one needs yet; a narrow API is also a smaller API.
- Supports **comprehensive error modeling** and **fail fast and loud** — a narrow operation has a small,
    well-defined error surface, so failures are easy to model and surface.
- Reinforces **clear, unambiguous, easily-parsed data models** — a single fixed operation naturally
    has a single fixed response schema.
