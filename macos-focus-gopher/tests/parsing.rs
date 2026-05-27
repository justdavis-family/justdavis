//! Integration test driving the pure parser against captured + synthesized
//! fixtures of `Assertions.json` / `ModeConfigurations.json`.
//!
//! These tests don't touch the filesystem at parse time — they `include_str!`
//! the fixture bodies at compile time and call [`parse_focus`] directly, which
//! is exactly the boundary the parser is designed for. The pipeline-level
//! tests in `tests/cli_roundtrip.rs` and `tests/socket_roundtrip.rs` exercise
//! the host's live database; this file pins the parser's deterministic
//! behavior on known inputs.
//!
//! See `tests/fixtures/FIXTURES.md` for an inventory of the captured shapes,
//! the PII scrubbing done before commit, and the known schedule-state
//! limitation on macOS 26.

use macos_focus_gopher::focus_db::{parse_focus, ParseFailure};
use macos_focus_gopher::model::Focus;

// --- focus_off ------------------------------------------------------------

const FOCUS_OFF_ASSERTIONS: &str = include_str!("fixtures/26/focus_off/Assertions.json");
const FOCUS_OFF_MODE_CONFIGURATIONS: &str =
    include_str!("fixtures/26/focus_off/ModeConfigurations.json");

#[test]
fn macos_26_focus_off_is_parsed_as_focus_off() {
    let focus = parse_focus(FOCUS_OFF_ASSERTIONS, FOCUS_OFF_MODE_CONFIGURATIONS)
        .expect("focus_off should parse cleanly");
    assert!(matches!(focus, Focus::FocusOff {}), "got {focus:?}");
}

// --- manual_focus_on_builtin (Do Not Disturb) -----------------------------

const MANUAL_BUILTIN_ASSERTIONS: &str =
    include_str!("fixtures/26/manual_focus_on_builtin/Assertions.json");
const MANUAL_BUILTIN_MODE_CONFIGURATIONS: &str =
    include_str!("fixtures/26/manual_focus_on_builtin/ModeConfigurations.json");

#[test]
fn macos_26_manual_focus_on_builtin_resolves_via_builtin_table() {
    let focus = parse_focus(
        MANUAL_BUILTIN_ASSERTIONS,
        MANUAL_BUILTIN_MODE_CONFIGURATIONS,
    )
    .expect("manual_focus_on_builtin should parse cleanly");
    match focus {
        Focus::FocusOn { name } => assert_eq!(name, "Do Not Disturb"),
        other => panic!("expected FocusOn(Do Not Disturb), got {other:?}"),
    }
}

// --- manual_focus_on_user (custom Focus, resolved via ModeConfigurations) -

const MANUAL_USER_ASSERTIONS: &str =
    include_str!("fixtures/26/manual_focus_on_user/Assertions.json");
const MANUAL_USER_MODE_CONFIGURATIONS: &str =
    include_str!("fixtures/26/manual_focus_on_user/ModeConfigurations.json");

#[test]
fn macos_26_manual_focus_on_user_resolves_via_mode_configurations() {
    let focus = parse_focus(MANUAL_USER_ASSERTIONS, MANUAL_USER_MODE_CONFIGURATIONS)
        .expect("manual_focus_on_user should parse cleanly");
    match focus {
        // The fixture's user-customized name was scrubbed to "Custom Focus C"
        // (see tests/fixtures/FIXTURES.md). The point of the test is that the
        // parser found the name in ModeConfigurations rather than the built-in
        // table — the literal name itself is incidental.
        Focus::FocusOn { name } => assert_eq!(name, "Custom Focus C"),
        other => panic!("expected FocusOn, got {other:?}"),
    }
}

// --- malformed (truncated JSON) -------------------------------------------

const MALFORMED_ASSERTIONS: &str = include_str!("fixtures/26/malformed/Assertions.json");
const MALFORMED_MODE_CONFIGURATIONS: &str =
    include_str!("fixtures/26/malformed/ModeConfigurations.json");

#[test]
fn macos_26_malformed_assertions_is_malformed() {
    let result = parse_focus(MALFORMED_ASSERTIONS, MALFORMED_MODE_CONFIGURATIONS);
    match result {
        Err(ParseFailure::Malformed { file, .. }) => assert_eq!(file, "Assertions.json"),
        other => panic!("expected Malformed, got {other:?}"),
    }
}

// --- schema_unknown -------------------------------------------------------

const SCHEMA_UNKNOWN_ASSERTIONS: &str = include_str!("fixtures/26/schema_unknown/Assertions.json");
const SCHEMA_UNKNOWN_MODE_CONFIGURATIONS: &str =
    include_str!("fixtures/26/schema_unknown/ModeConfigurations.json");

#[test]
fn macos_26_schema_unknown_returns_schema_unknown() {
    // The synthesized schema_unknown fixture is a non-object JSON root
    // (`[1,2,3]`) — structurally legal JSON but not the shape `Assertions.json`
    // is ever supposed to take. The parser must refuse to interpret it rather
    // than silently report "Focus off"; see the "Fail Fast and Loud" and
    // "Clear, Unambiguous Data Models" engineering principles.
    let result = parse_focus(
        SCHEMA_UNKNOWN_ASSERTIONS,
        SCHEMA_UNKNOWN_MODE_CONFIGURATIONS,
    );
    assert!(
        matches!(result, Err(ParseFailure::SchemaUnknown { .. })),
        "expected SchemaUnknown, got {result:?}",
    );
}

// --- name_unresolved ------------------------------------------------------

const NAME_UNRESOLVED_ASSERTIONS: &str =
    include_str!("fixtures/26/name_unresolved/Assertions.json");
const NAME_UNRESOLVED_MODE_CONFIGURATIONS: &str =
    include_str!("fixtures/26/name_unresolved/ModeConfigurations.json");

#[test]
fn macos_26_name_unresolved_returns_name_unresolved() {
    let result = parse_focus(
        NAME_UNRESOLVED_ASSERTIONS,
        NAME_UNRESOLVED_MODE_CONFIGURATIONS,
    );
    match result {
        Err(ParseFailure::NameUnresolved(id)) => {
            assert_eq!(id, "com.example.unknown-mode");
        }
        other => panic!("expected NameUnresolved, got {other:?}"),
    }
}
