//! Built-in Focus identifier → human-readable name table.
//!
//! macOS ships a set of well-known Focus identifiers under `com.apple.…`. For
//! these we know the display name without needing to consult
//! `ModeConfigurations.json`, which (a) is a small reliability win when that
//! file is missing or stale and (b) gives stable English names even on a system
//! whose UI is localized differently (the helper's wire output is English by
//! design).
//!
//! User-created Foci are *not* in this table — they live in
//! `ModeConfigurations.json` and are resolved there.

/// Resolve a built-in Focus identifier (e.g. `"com.apple.donotdisturb.mode.default"`)
/// to its English display name (e.g. `"Do Not Disturb"`), or `None` if the
/// identifier is not a known built-in.
pub fn builtin_name(identifier: &str) -> Option<&'static str> {
    match identifier {
        "com.apple.donotdisturb.mode.default" => Some("Do Not Disturb"),
        "com.apple.sleep.sleep-mode" => Some("Sleep"),
        "com.apple.focus.personal-time" => Some("Personal"),
        "com.apple.focus.work" => Some("Work"),
        "com.apple.donotdisturb.mode.workout" => Some("Fitness"),
        "com.apple.donotdisturb.mode.driving" => Some("Driving"),
        "com.apple.focus.reduce-interruptions" => Some("Reduce Interruptions"),
        "com.apple.focus.gaming" => Some("Gaming"),
        "com.apple.focus.mindfulness" => Some("Mindfulness"),
        "com.apple.focus.reading" => Some("Reading"),
        _ => None,
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn known_identifiers_resolve() {
        let cases = [
            ("com.apple.donotdisturb.mode.default", "Do Not Disturb"),
            ("com.apple.sleep.sleep-mode", "Sleep"),
            ("com.apple.focus.work", "Work"),
            ("com.apple.donotdisturb.mode.driving", "Driving"),
        ];
        for (id, expected) in cases {
            assert_eq!(builtin_name(id), Some(expected));
        }
    }

    #[test]
    fn unknown_identifier_returns_none() {
        assert_eq!(builtin_name("com.example.unknown-mode"), None);
        assert_eq!(builtin_name(""), None);
    }
}
