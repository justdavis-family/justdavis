# macOS Focus Database Format and Stability

## Question

The [macOS Focus Gopher](../engineering-designs/2026-05-12-macos-focus-gopher.md) reads the current
  Focus state from undocumented files under the user's home directory.
Before committing to that approach — and before seeding the helper's macOS-version compatibility table —
  we want to know:

1. Where does macOS store Focus / Do Not Disturb state, and in what format?
2. How long has that format existed, and how stable has it been across macOS releases?
3. Can we reasonably support whole *major* macOS versions with a wildcard entry in the compatibility
     table, or should we only ever claim support for specific point releases we have verified?

## Findings

### 1. Where the State Lives, and the Format

Since **macOS 12 Monterey** (when "Focus" replaced the older standalone "Do Not Disturb"),
  the state lives in JSON files under `~/Library/DoNotDisturb/DB/`, principally:

- `Assertions.json` — the *active* state.
    An active Focus shows up as an entry under `data[0].storeAssertionRecords`,
    whose `assertionDetails.assertionDetailsModeIdentifier` (e.g. `com.apple.focus.personal-time`,
    or a UUID for a user-created Focus) identifies which mode is on.
    When no Focus is manually active the file is effectively empty
    (an empty object, or a `data` array with no assertion records).
- `ModeConfigurations.json` — the *configured* modes: a `data[0].modeConfigurations` map keyed by mode
    UUID, each entry carrying the mode's human-readable `name`, symbol, and its triggers/schedule.
    This is also where a *schedule- or automation-activated* Focus is reflected
    (via the mode's trigger/`enabled` state), as opposed to a manual activation,
    which appears in `Assertions.json` — a parser must consult both to get the full picture.

Mapping an active identifier from `Assertions.json` to a display name requires cross-referencing
  `ModeConfigurations.json` (and, for built-in Foci, a fixed identifier→name table).

Before macOS 12 (Big Sur and earlier), Do Not Disturb was *not* stored this way — it lived in
  Notification Center preference plists (e.g. `com.apple.ncprefs.plist`) with an entirely different
  structure. That older mechanism is out of scope for this project; supporting it would require a
  separate parser and is not planned.

### 2. How Long the Format Has Existed, and How Stable It Has Been

The `~/Library/DoNotDisturb/DB/` JSON layout has been in place since macOS 12 (2021) and has been
  relied on by a steady stream of community tools across macOS 12 Monterey, 13 Ventura, 14 Sonoma,
  and 15 Sequoia without the core shape changing:

- A widely-copied JXA snippet for reading the current Focus
    ([drewkerr gist](https://gist.github.com/drewkerr/0f2b61ce34e2b9e3ce0ec6a92ab05c18)).
- CLI tools such as [`davidolrik/getfocus`](https://github.com/davidolrik/getfocus) and
    [`legnoh/focus-cli`](https://github.com/legnoh/focus-cli).
- A detailed write-up of the file structure and the manual-vs-scheduled-activation wrinkle
    ([brunerd, "Respecting Focus and Meeting Status in Your Mac scripts"](https://www.brunerd.com/blog/2022/03/07/respecting-focus-and-meeting-status-in-your-mac-scripts-aka-dont-be-a-jerk/)).
- Long-running community threads tracking the approach across releases
    ([Automators forum](https://talk.automators.fm/t/get-current-focus-mode-via-script/12423)).

Caveats the same sources surface, which a robust parser must handle:

- "No Focus active" is represented by an *empty/near-empty* `Assertions.json`, not by an explicit
    "off" record — so an empty file is a valid, successful "Focus is off" result, not an error.
- Manually-toggled Focus vs. schedule/automation-activated Focus appear in different files
    (`Assertions.json` vs. a trigger state in `ModeConfigurations.json`).
- Files can be momentarily absent or partially written while macOS updates them.
- The format is still **undocumented and unsupported by Apple**; nothing prevents a future macOS
    release from changing it.

We did not find authoritative confirmation of the format on the current **macOS 26 Tahoe** release;
  it is presumed similar but should be treated as unverified until we test it.

### 3. Specific Point Releases vs. Major-Version Wildcards

Because the format is undocumented, the conservative default is to claim support only for versions we
  have actually exercised. However, the evidence above is strong enough that the *major-version*
  granularity is a reasonable unit for macOS 12–15: the layout has survived four major releases of
  active community use without a breaking change, and Apple has shown no sign of reworking it.

Recommendation:

- The compatibility table is **keyed by macOS version string**, and an entry may be either a specific
    point release (e.g. `15.5`) or a major-version wildcard (e.g. `15.*`).
- A **major-version wildcard entry is allowed only when** (a) this analysis (or a future update to it)
    finds the format stable for that major, and (b) the helper's parser has been verified against at
    least one *current* point release of that major. On that basis, `12.*`–`15.*` are reasonable
    `supported` entries once verified.
- macOS **11 and earlier** are out of scope (different mechanism).
- macOS **26** (and any future major) starts as `unknown until tested`; it is reported with the
    `unknown` compatibility variant (carrying a "please report whether this version works" message)
    until added to the table — whether parsing actually worked is conveyed by the result's outcome, not
    the compatibility field.

This analysis should be revisited whenever a new major macOS release ships, or whenever the parser
  encounters a `schema_unknown` failure in the field.

## References

- **Product Requirement**: [macOS Focus Gopher](../product-requirements/2026-05-12-macos-focus-gopher.md).
- **Engineering Design**: [macOS Focus Gopher Engineering Design](../engineering-designs/2026-05-12-macos-focus-gopher.md).
- Sources:
  - [Read the current Focus mode on macOS Monterey (12.0+) using JXA — drewkerr gist](https://gist.github.com/drewkerr/0f2b61ce34e2b9e3ce0ec6a92ab05c18).
  - [davidolrik/getfocus](https://github.com/davidolrik/getfocus).
  - [legnoh/focus-cli](https://github.com/legnoh/focus-cli).
  - [brunerd — Respecting Focus and Meeting Status in Your Mac scripts](https://www.brunerd.com/blog/2022/03/07/respecting-focus-and-meeting-status-in-your-mac-scripts-aka-dont-be-a-jerk/).
  - [Automators forum — Get current focus mode via script](https://talk.automators.fm/t/get-current-focus-mode-via-script/12423).
