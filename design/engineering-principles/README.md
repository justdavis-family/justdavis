# Engineering Principles

Engineering principles...

- Capture recurring patterns and hard-learned lessons about
    how to build reliable, maintainable software.
- In order to guide architectural choices, engineering design, and code reviews.

**Key distinction from other [`design/`](../) docs:**

- **Product Vision docs** capture what we're building and why.
- **Engineering Design docs** capture specific technical approaches for features.
- **Engineering Principle docs** capture how we approach engineering problems in general.

## Current Engineering Principles

The current engineering principles are documented in individual files within this directory.
Each engineering principle follows a consistent format to ensure clarity and ease of use.

Also, the [`.claude/rules/engineering-principles.md`](/.claude/rules/engineering-principles.md)
  file contains an up-to-date index of all the engineering principles,
  and should be updated whenever a new engineering principle is added
  or when an existing engineering principle is modified.
Maintain the index's existing relevance, brevity, and format.

## Using the Engineering Principles

**In design discussions:**

- Reference the engineering principles when evaluating options.
- Explain when and why you're violating an engineering principle (with justification).

**In code reviews:**

- Point to the engineering principles rather than stating personal preferences.
- Remember the engineering principles are guidelines, not absolute rules.

**When engineering principles conflict:**

- Acknowledge the trade-off explicitly.
- Document the decision and rationale.
- Consider whether the conflict reveals a gap in our engineering principles.

## Adding New Engineering Principles

When you notice a recurring pattern or decision-making criterion
  in code reviews or design discussions,
  consider whether it should be captured as an engineering principle:

1. **Is it generalizable?** Does it apply across multiple features or components?
2. **Is it non-obvious?** Would a new contributor benefit from knowing this?
3. **Does it have trade-offs?** Are there legitimate cases where you'd violate it?

If yes to all three, it's likely worth documenting as an engineering principle.

### Template

Use [`template.md`](template.md) as a starting point
  for new engineering principle documents.
The template includes sections for Principle, Rationale, Examples,
  When to Break This Rule, and Relationship to Other Principles.

See [../README.md](../README.md) for file naming conventions
  and general document structure guidelines.
