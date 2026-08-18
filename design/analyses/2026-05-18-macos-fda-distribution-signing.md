# macOS Full Disk Access, Code Signing, and Distribution Channels

## Question

The [macOS Focus Gopher](../engineering-designs/2026-05-12-macos-focus-gopher.md) helper reads a
  TCC-protected location (the Focus database under `~/Library/DoNotDisturb/DB/`),
  which in practice requires the helper itself to hold **Full Disk Access (FDA)**.
The original design assumed the helper would always be shipped as a
  **code-signed and notarized `.app` bundle**.
Before committing build, signing, and distribution effort, we want to know:

1. What do code signing and notarization actually buy us, and what do they *not*?
2. How does each preferred distribution channel — `cargo install` and Homebrew
     (formula, tap, cask) — interact with signing, notarization, and the FDA grant?
3. Can the helper detect and gracefully handle a missing FDA grant,
     regardless of how it was distributed?
4. Given the answers, what must early milestones do, and what can be deferred?

## Findings

### 1. The Three macOS Mechanisms in Play

- **Code-signing identity (what TCC uses to recognize "the same app" across updates).**
  A **Developer ID** signature (a certificate held by the publisher; requires the paid Apple Developer
    Program) makes TCC key the grant off the app's *Designated Requirement*
    (bundle ID + Team ID), which is stable across rebuilds and versions —
    so the FDA grant **persists across updates**.
  An **unsigned or ad-hoc** binary (what a local compile produces by default;
    Apple Silicon requires at least ad-hoc) is recognized by TCC via the binary's **cdhash**
    (a content hash), which changes on every rebuild —
    so the grant is **invalidated on every update** and must be re-granted.
- **Notarization.**
  The publisher uploads a Developer-ID-signed artifact to Apple for an automated malware scan,
    then staples the returned ticket.
  It requires Developer ID signing first (an unsigned/ad-hoc build cannot be notarized)
    and the paid Apple Developer Program.
- **Quarantine + Gatekeeper.**
  The `com.apple.quarantine` attribute is set on *downloaded* artifacts.
  On first launch of a quarantined artifact, Gatekeeper requires it to be Developer-ID-signed
    **and** notarized, or it is blocked / shown a scary warning.
  Locally compiled artifacts are **not** quarantined,
    so Gatekeeper never gates them and **notarization is irrelevant** for them.

The crux: notarization only matters *if the artifact is quarantined*,
  and persistent FDA only happens *if the publisher ships its own stable Developer ID signature*.
A from-source build cannot carry the publisher's signature (it is built on the user's machine),
  so realistically it is a binary choice:
  a **signed + notarized prebuilt** artifact, or an **unsigned/ad-hoc from-source** build.

### 2. Full Disk Access Can Never Be Granted Programmatically

There is no `requestAuthorization`-style API that prompts for, and grants, Full Disk Access —
  on any channel or signing state.
The first-time FDA grant is **always** a manual trip to
  System Settings → Privacy & Security → Full Disk Access.
A signed, notarized, App Store app still requires this.

This is specific to FDA (and its raw-disk siblings).
Narrower scopes — Desktop, Documents, Downloads, removable/network volumes, Contacts, Calendar,
  Photos, and similar — *do* have inline consent prompts whose "Allow" grants that scope immediately.
The Focus database falls under broad FDA, not these friendlier per-folder prompts.

What signing *does* improve here is **discoverability of the need**, not the grant itself — and it is
  a pure side channel that the app never sees.
In **both** the signed and unsigned cases the FDA-gated operation itself fails identically: the app
  receives an `EPERM` and nothing more.
The difference is what macOS does *alongside* that failure, out of band: for a **properly code-signed
  app with a bundle identity**, the system often raises a *redirect* dialog
  ("…go to System Settings", with an **Open System Settings** button) and pre-lists the app in the Full
  Disk Access pane (toggled off, ready to flip); for a bare **unsigned/ad-hoc CLI binary** (the
  build-from-source case) it typically raises no dialog and adds no pre-listing.
The app cannot observe, trigger, or depend on that dialog either way — it only ever sees the `EPERM` —
  so this is purely a human-facing convenience, not anything the helper's own error handling can lean on.
This is why signed apps (iTerm, Ghostty, Terminal) get OS signposting toward the FDA pane
  while ad-hoc command-line tools tend to fail silently.

Note: the exact redirect-dialog behavior (when it fires, for which signing state, per macOS major)
  is version-sensitive and should be empirically verified on device
  rather than asserted categorically.

### 3. Detecting a Missing FDA Grant (`EPERM` vs. `ENOENT`)

There is **no API to query the helper's own FDA status**; detection is necessarily *reactive*
  (attempt the read, interpret the failure).

- File exists, FDA held → `open()` succeeds.
- File exists, FDA **not** held → `open()` returns **`EPERM`** ("Operation not permitted"),
    *not* `ENOENT`.
  This is the dependable "no FDA" signal on the primary read path.
- File genuinely absent (Focus never configured) → `ENOENT` —
    *but* `~/Library/DoNotDisturb` is a TCC-gated directory,
    so when the process is unprivileged the gate can convert a would-be `ENOENT` into `EPERM`
    (denied before existence can be revealed).
  Directory enumeration without FDA is gated the same way (no trustworthy "empty directory").

Therefore `EPERM` reliably means "denied" (overwhelmingly: no FDA),
  while `ENOENT` is only trustworthy as "absent" once access is already confirmed.
The benign "Focus is off" state is represented by *empty file content*, not file absence,
  so it is an `open()`-success-plus-empty case, not an `ENOENT` case
  (see the [format-stability analysis](2026-05-12-macos-focus-db-format.md)).

This detection works **on every channel and signing state** — it is unaffected by not signing.
Per [Comprehensive Error Modeling](../engineering-principles/2026-01-08-error-modeling.md) and
  [Clear, Unambiguous, Easily-Parsed Data Models](../engineering-principles/2026-05-12-clear-data-models.md),
  the denied case must surface as its **own dedicated error code** (`focus_permission_denied`, a
  `failed` outcome) with actionable, deep-linked remediation in the `failed` variant's `message` (the
  resolved binary path to add, and the
  `x-apple.systempreferences:com.apple.preference.security?Privacy_AllFiles` deep link),
  and must **never** be collapsed into a `determined` result.
The message should print the *canonical resolved* executable path
  (cargo and Homebrew both symlink into `bin/`, and TCC matches the real binary,
  so naming the symlink can misfire).

### 4. Per-Channel Impact

| Channel | Quarantined? | Notarization | Signature the publisher can ship | FDA across updates | Apple acct |
| --- | --- | --- | --- | --- | --- |
| `cargo install` | No | N/A | ad-hoc only (local build) | Re-grant each update | No |
| Homebrew formula | No | N/A | ad-hoc only (local build / Homebrew-CI bottle) | Re-grant each update | No |
| Homebrew tap | inherits | inherits | inherits | inherits | inherits |
| Homebrew cask | **Yes** | **Required** | **Developer ID** (prebuilt) | **Persists** | **Yes ($99/yr)** |

- **`cargo install`** compiles on the user's machine and installs a bare binary into `~/.cargo/bin/`
    (not an `.app`, not a LaunchAgent).
  Not quarantined (notarization irrelevant); ad-hoc identity (FDA re-granted every upgrade);
    no Apple account; the worst case for first-run signposting (often silent `EPERM`).
- **Homebrew formula** builds from source on the user's machine (or installs a Homebrew-CI-built
    bottle); either way the artifact is not quarantined and not publisher-signed —
    functionally equivalent to the `cargo install` story for our purposes.
- **Homebrew tap** is a *delivery vehicle*, not a packaging type:
    a third-party repo containing a formula or a cask.
  It changes nothing about signing/notarization; it inherits the behavior of whatever it contains.
  It is relevant only because this project will not be in homebrew-core
    (third-party notability rules), so a tap is the realistic channel either way.
- **Homebrew cask** installs a prebuilt artifact the publisher produces and hosts.
  Homebrew **quarantines casks by default**, so the `.app` is Gatekeeper-gated on first launch and
    must, in practice, be Developer-ID-signed **and** notarized
    (the `--no-quarantine` escape hatch is a security smell and a poor default for an FDA tool).
  Because it ships the publisher's stable Developer ID signature,
    this is the **only** channel where the FDA grant persists across updates
    and where the OS redirect dialog reliably appears.

### 5. What Signing + Notarization Actually Buys This Project

- **FDA persists across updates** (stable Developer ID identity vs. per-build cdhash) —
    the only channel that delivers this is the signed + notarized **cask**.
- **Better first-run discoverability** — the OS redirect dialog and FDA-pane pre-listing
    fire for signed bundles, where the bare-binary channels often fail silently.
- **Clears the Gatekeeper launch wall** that a quarantining **cask** would otherwise hit
    (a notarization-only benefit, irrelevant to the non-quarantined from-source channels).

It does **not** enable programmatic FDA granting,
  and it does **not** remove the one-time manual System Settings step on any channel.

### 6. Developing and Testing Locally without a Developer ID Signature

Because an unsigned/ad-hoc binary's TCC identity is its cdhash,
  every rebuild produces a new identity and invalidates the Full Disk Access grant —
  *even when the binary is rebuilt in place at a stable path*.
A naive inner loop (build → run as a LaunchAgent against the live database → repeat) would therefore
  require re-adding the binary in System Settings after every build,
  which would make local development of this project genuinely painful.

Three things defuse this, and together they should be the documented default workflow:

- **Fixtures need no FDA.**
  The fixture-based test strategy (captured `Assertions.json` / `ModeConfigurations.json` files in the
    repo, not the TCC-protected path) means the bulk of the unit/integration suite reads ordinary files
    and never touches TCC.
  Full Disk Access is exercised only by live smoke tests and the end-to-end test.
- **A self-signed local code-signing certificate gives a stable identity with no Apple account.**
  A one-time Keychain step creates a self-signed code-signing certificate;
    signing dev builds with it (`codesign -s "<local cert>"`) yields a stable TCC *Designated
    Requirement* on the developer's machine, so the FDA grant **persists across rebuilds** —
    the same property the shipped product only gains at M6, achievable locally for free.
  This matters most for LaunchAgent-shape testing, where access is attributed to the helper binary
    itself rather than to a parent process.
- **Granting FDA to the responsible parent process covers run-from-terminal iteration.**
  When the helper is run directly (not via the LaunchAgent), TCC attributes file access to the
    responsible parent process, so granting Full Disk Access once to the developer's terminal/IDE lets
    anything launched from it read the protected files without per-build re-granting.
  (This grants broad FDA to that terminal — acceptable on a dev machine, and never part of the shipped
    artifact.)

The genuinely painful scenario occurs only if a developer uses none of these and tests exclusively
  through the LaunchAgent path against the live database.
The self-signed-certificate and responsible-process behaviors are the established approaches but are
  version-sensitive, and belong in the same on-device verification bucket as the rest of this analysis.

## Recommendation

- Treat **code signing + notarization** (and a **cask** channel) as
    *nice-to-have UX improvements*, not prerequisites for usefulness.
  Defer them to a **final, optional milestone** that may or may not be reached.
- Target **build-from-source** distribution (`cargo install`, Homebrew formula/tap) for the
    earlier milestones: no Apple Developer account, no notarization,
    accepting that the user re-grants FDA after each upgrade
    and that the helper's own error message is the primary first-run signpost.
- Make **graceful missing-FDA handling a first-class, early requirement**:
    a dedicated permission-denied error code,
    an actionable deep-linked `message` (resolved binary path + Settings deep link),
    and `README`/`--help`/`man` documentation of exactly how to grant FDA
    (including that it must be re-granted after upgrades on the from-source channels).
- Keep the **bundle / stable-identity architecture** (LaunchAgent and `.app` layout) intact;
    only the Developer ID **signature + notarization** and the **cask** channel are deferred.
- **Document the local-development workflow** (fixtures-need-no-FDA, a self-signed dev signing
    certificate, and terminal/responsible-process FDA), and ship a dev build task that signs with the
    local certificate so it is the default path rather than tribal knowledge.
  Capture it in the contributor docs of the first milestone that reads the protected files,
    and again in the first milestone that builds the user LaunchAgent.

This analysis should be revisited if the project gains an Apple Developer Program membership,
  if a cask channel is pursued, or if on-device verification contradicts the
  `EPERM`/redirect-dialog behavior described here.

## References

- **Product Vision**: [macOS Focus Gopher](../product-vision/2026-05-12-macos-focus-gopher.md).
- **Product Requirement**: [macOS Focus Gopher](../product-requirements/2026-05-12-macos-focus-gopher.md).
- **Engineering Design**: [macOS Focus Gopher Engineering Design](../engineering-designs/2026-05-12-macos-focus-gopher.md).
- **Delivery Plan**: [macOS Focus Gopher Delivery Plan](../delivery-plans/2026-05-12-macos-focus-gopher.md).
- **Related Analyses**:
    [macOS Focus Database Format and Stability](2026-05-12-macos-focus-db-format.md);
    [`FocusState` JSON Response Shape: Flat vs. Tagged Union](2026-05-12-focus-state-json-shape.md).
- **Engineering Principles**:
    [Least Privilege](../engineering-principles/2026-05-12-least-privilege.md);
    [Comprehensive Error Modeling](../engineering-principles/2026-01-08-error-modeling.md);
    [Clear, Unambiguous, Easily-Parsed Data Models](../engineering-principles/2026-05-12-clear-data-models.md);
    [YAGNI](../engineering-principles/2026-01-06-yagni.md).
- macOS TCC / Gatekeeper / notarization behavior described here reflects established platform behavior
    as of this writing; the version-exact `EPERM` and redirect-dialog specifics
    are flagged for empirical verification during the on-device milestones (see the delivery plan).
