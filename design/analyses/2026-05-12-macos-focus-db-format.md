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

### 1. Where the state lives, and the format

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

### 2. How long the format has existed, and how stable it has been

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

**macOS 26.4.1 and macOS 26.5 have both been verified** against the Focus Gopher parser.
The committed test fixtures
  (see [`macos-focus-gopher/tests/fixtures/26.4.1/`](../../macos-focus-gopher/tests/fixtures/) and
  [`FIXTURES.md`](../../macos-focus-gopher/tests/fixtures/FIXTURES.md))
  were captured on macOS 26.4.1, which is the version `tests/parsing.rs` exercises.
On macOS 26.5, the parser has additionally been verified via live e2e
  of four manual-Focus scenarios:
  no Focus active (`focus_off`), a built-in Focus active (Do Not Disturb, Work),
  a user-created Focus active (resolved via `ModeConfigurations.json` name lookup),
  and the back-to-no-Focus transition.
No other macOS 26 point release has been independently verified in this codebase,
  and — per the bullet above —
  Apple may change the private format in any point release within a major,
  so claims about "macOS 26 as a series" should not be inferred from these verifications.
The layout observed on 26.4.1 matches the structure reported by community tools
  running on individual point releases of macOS 12 Monterey, 13 Ventura, 14 Sonoma,
  and 15 Sequoia (see the citations in section 2):
  a manually-toggled Focus appears as a
  `storeAssertionRecords[0].assertionDetails.assertionDetailsModeIdentifier`
  entry in `Assertions.json`,
  and `ModeConfigurations.json` is a `data[0].modeConfigurations` map keyed by **mode identifier**
  (e.g. `com.apple.focus.work`, *not* a UUID
  — the analysis previously described it as UUID-keyed;
  that was incorrect for at least macOS 26.4.1,
  and likely for the earlier majors too based on the community-report wording).

> ### Schedule-triggered Foci on macOS 26.4.1 — a new finding
>
> While capturing fixtures for Focus Gopher's first parsing milestone we observed that on
>   macOS 26.4.1, a Focus activated by a *user-defined schedule trigger* does **not** appear
>   in any file under `~/Library/DoNotDisturb/DB/`.
> `Assertions.json`'s `storeAssertionRecords` stays empty, `Settings.sqlite`'s Focus tables stay
>   empty, and no preference plist or cache surfaces the active state.
> The most likely explanation is that `donotdisturbd` keeps schedule-triggered state in memory
>   and exposes it only via XPC.
>
> This contradicts the section above's expectation
>   ("manually-toggled Focus vs. schedule/automation-activated Focus appear in different files
>   (`Assertions.json` vs. a trigger state in `ModeConfigurations.json`)") in the macOS 26.4.1 case:
>   `ModeConfigurations.json`'s `triggers[].enabledSetting` is a configuration value, not a
>   runtime state.
>
> Other macOS 26 point releases have not been separately re-tested for this gap.
> Per the per-version policy recommended in section 3
>   and specified in the
>   [engineering design](../engineering-designs/2026-05-12-macos-focus-gopher.md),
>   the finding should not be generalized to "macOS 26 as a series" without re-verification
>   on the additional point releases.
> Whether earlier majors (12–15) still write schedule-activated assertions to
>   `Assertions.json` (per the historical community reports) also needs separate verification.
>
> File-based detection of schedule-triggered Foci on the macOS 26.4.1 host we observed is
>   therefore a known gap; the manual-activation path works correctly.
> The gap is tracked in the project issue tracker.

### 3. Recommended policy for the compatibility table

The Focus database format is private and undocumented,
  and Apple can change it in any point release within a major version.

A *major-version wildcard* policy would extrapolate from one verified point release
  to a whole major
  — asserting coverage of point releases we have not exercised,
    in a context where exercising each release is the only way to be sure
    the format hasn't shifted.
That overclaims.

An *exact-version* policy reports only what we have actually checked,
  at the cost of more `unknown` results on unverified point releases.
The cost is real:
  a modern macOS major ships roughly 10–15 distinct point versions over its active-support window
  (e.g. `14.0` through `14.7.x`,
    where each `.x` may also get one or more patch releases such as `14.4.1`),
  plus several more during extended security support after the next major takes over.
That cadence is the **work item for compatibility coverage**
  — growing the verified list as contributors verify additional versions —
  not a cost to be avoided by claiming wider coverage than we actually have.

The format-stability evidence in section 2 — community tools running on individual point releases
  of macOS 12 Monterey, 13 Ventura, 14 Sonoma, and 15 Sequoia without a major reshape,
  plus this codebase's own verification on the macOS 26 versions we have checked —
  suggests that Apple's *typical* behavior preserves the format across point releases within a major.
That is a probabilistic observation, not a guarantee,
  and so the recommended policy still treats each point release as needing its own verification.

**Recommendation:** an exact-version policy.
The detailed semantics (match rules, unknown-message content,
    the workflow for adding entries, the implementation)
  and the source-of-truth list of currently-verified versions live in the
  [engineering design](../engineering-designs/2026-05-12-macos-focus-gopher.md)
  and `compatibility.rs`;
  this section provides the evidence and reasoning that support that recommendation.

This analysis should be revisited whenever a new major macOS release ships,
  or whenever the parser encounters a `schema_unknown` or `focus_db_malformed` failure in the field.

## References

- **Product Requirement**: [macOS Focus Gopher](../product-requirements/2026-05-12-macos-focus-gopher.md).
- **Engineering Design**: [macOS Focus Gopher Engineering Design](../engineering-designs/2026-05-12-macos-focus-gopher.md).
- Sources:
  - [Read the current Focus mode on macOS Monterey (12.0+) using JXA — drewkerr gist](https://gist.github.com/drewkerr/0f2b61ce34e2b9e3ce0ec6a92ab05c18).
  - [davidolrik/getfocus](https://github.com/davidolrik/getfocus).
  - [legnoh/focus-cli](https://github.com/legnoh/focus-cli).
  - [brunerd — Respecting Focus and Meeting Status in Your Mac scripts](https://www.brunerd.com/blog/2022/03/07/respecting-focus-and-meeting-status-in-your-mac-scripts-aka-dont-be-a-jerk/).
  - [Automators forum — Get current focus mode via script](https://talk.automators.fm/t/get-current-focus-mode-via-script/12423).
