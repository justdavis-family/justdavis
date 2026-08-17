# Analyses

This directory contains engineering and technical analysis documents
  for projects in this monorepo.

These analyses evaluate options, trade-offs, and potential solutions
  to inform product and engineering decisions.

## When to Write an Analysis

Analyses come *before* the design decisions they inform, and exist to evaluate options.
Write one when a significant decision has multiple viable options,
  or when a design would otherwise rest on facts nobody has actually checked
  — an undocumented file format, a third-party API's real behavior,
  whether an approach is even feasible.

Straightforward choices don't need one.
The test is whether a reader would otherwise have to take the conclusion on faith.

## What Makes a Good Analysis

- **Durable.** Analyses are committed and cross-linked from the designs they inform,
    because they explain *why* a design is what it is
    long after the rejected alternatives have been forgotten.
  Exploratory thinking that isn't ready for that belongs in [`../notes/`](../notes/).
- **Honest about provenance.** If a claim was inherited from elsewhere rather than verified,
    say so plainly, and say what would settle it.
  An analysis that launders assumptions into apparent facts is worse than no analysis,
    because the design built on it will look better-grounded than it is.
- **Decision-forcing.** State what the analysis concludes and what it implies for the design,
    rather than surveying options and leaving the reader to choose.

## Naming Convention

See [../README.md](../README.md) for file naming conventions
  and general document structure guidelines.
