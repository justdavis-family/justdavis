# Focus database fixtures

Real captures and synthesized variants of `Assertions.json` and `ModeConfigurations.json`
  driving the fixture-based parser tests
  in [`tests/parsing.rs`](../parsing.rs).

## Layout

```
fixtures/
  <macos_version>/
    <case>/
      Assertions.json
      ModeConfigurations.json
```

`<macos_version>` is the specific macOS version the fixtures were captured from
  (e.g. `26.4.1`),
  matching the per-version compatibility policy in the
  [engineering design](../../../design/engineering-designs/2026-05-12-macos-focus-gopher.md).
Whichever `<macos_version>/` directories are present in this tree are the current set.
In practice, point releases within a major often produce functionally identical fixtures,
  so a new `<macos_version>/` directory is only added
  when a verified macOS version shows meaningful differences from existing captures.

For versions that have been live-verified without recapturing
  (because they share the format of an existing captured version),
  the format-stability analysis records each live-verification individually
  and is the source of truth for which macOS versions have been verified at all.

## Cases

| Case                     | Source       | Expected parser result                              |
| ------------------------ | ------------ | --------------------------------------------------- |
| `focus_off`              | Real         | `Focus::FocusOff`                                   |
| `manual_focus_on_builtin`| Real         | `Focus::FocusOn { name: "Do Not Disturb" }`         |
| `manual_focus_on_user`   | Real         | `Focus::FocusOn { name: "Custom Focus C" }`         |
| `malformed`              | Synthesized  | `ParseFailure::Malformed`                           |
| `schema_unknown`         | Synthesized  | `ParseFailure::SchemaUnknown`                       |
| `name_unresolved`        | Synthesized  | `ParseFailure::NameUnresolved(_)`                   |

Real captures are taken directly from `~/Library/DoNotDisturb/DB/`
  with the host's Focus state set to match the case.
Synthesized fixtures are derived from a real capture (or hand-written as the
  smallest possible body that exercises the target path):
  truncating, swapping in a non-object JSON root, or removing a matching mode
  entry from `ModeConfigurations.json`.

## PII scrubbing

The real captures were scrubbed before commit:

- All UUIDs (device identifiers, per-assertion identifiers, mode identifiers) were replaced
    with deterministic placeholders of the form
    `00000000-0000-0000-0000-000000000NNN`, numbered in order of first appearance.
- User-customized mode names were replaced with generic labels:
  - `"Vroom Vroom"` → `"Custom Focus A"`
    (mode identifier `com.apple.donotdisturb.mode.bicycle`).
  - `"Meeting"` → `"Custom Focus B"`
    (mode identifier `com.apple.donotdisturb.mode.bubbleleftfill`).
  - `"Relaxing"` → `"Custom Focus C"`
    (mode identifier `com.apple.donotdisturb.mode.emojifacegrinning`).
- Apple built-in mode names (`Sleep`, `Do Not Disturb`, `Work`, etc.) and mode identifiers
    (the `com.apple.…` strings, including the SF Symbol fragments) are left as-is —
    they are stable Apple identifiers, not personal data.
- Timestamps are left as-is — they are not identifying on their own.

## Known limitation: schedule-triggered Foci

**Versions confirmed:** macOS 26.4.1.
Not separately re-tested on other versions;
  it is plausible the behavior is the same on, e.g., macOS 26.5,
  but we do not currently have positive or negative evidence either way.

When a Focus is activated by a user-defined schedule trigger,
  no file under `~/Library/DoNotDisturb/DB/` reflects the active state:
  `Assertions.json`'s `storeAssertionRecords` array remains empty,
    `Settings.sqlite`'s Focus tables stay empty,
    and neither `Metrics.json` nor any preference plist surfaces it.

The most likely explanation is that `donotdisturbd` keeps schedule-triggered
  state in memory and exposes it only via XPC.

For this reason, the current fixture set ships **without** a
  `scheduled_focus_on` fixture: the parser path that handles a
  `storeAssertionRecord` (used by `manual_focus_on_builtin` and
  `manual_focus_on_user`) is the same one a schedule trigger would exercise
  on older macOS versions where the format-stability analysis says scheduled
  assertions DO appear in `Assertions.json`.
This gap is tracked in the project issue tracker and will be revisited later.
