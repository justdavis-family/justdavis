# Markdown Style

All markdown files follow standardized formatting rules.

## Line Structure

- One sentence per line for better version control.
- 110-character line wrap limit at natural break points.
- Meet the line length limit with whitespace changes only
    (line breaks and continuation indentation);
    never alter content to shorten a line.
- Some elements will consistently exceed the limit and that's fine,
    e.g., URLs, Markdown links, Markdown table rows,
    and reference-style link definitions.
- POSIX line endings.
- Trailing whitespace removal (except when required by Markdown).

## Continuation Indentation

Indent wrapped lines 2 spaces past where text begins (count prefix chars + 2):

- Regular prose: 2 spaces (no prefix, text at column 1, indent to column 3).
- List items (`- ` = 2 chars, text at column 3): 4 spaces (indent to column 5).
- Checklist items (`- [ ] ` = 6 chars, text at column 7): 8 spaces (indent to column 9).

## Punctuation

End all sentence-like lines with periods, including:

- Regular prose sentences.
- List items (bullet points and numbered lists).
- Checklist items (todo entries).
- Table cells containing full sentences.
- Code comments in markdown code blocks (follow language conventions).

## Examples

Wrapping regular prose (2 spaces):

```
The quick brown fox
  jumped over the lazy dog.
```

Wrapping list items (4 spaces — aligning with text after `- `):

```
- The quick brown fox
    jumped over the lazy dog.
```

Wrapping checklist items (8 spaces — 2 past text start):

```
- [ ] The quick brown fox
        jumped over the lazy dog.
```

Visual guide for checklist indentation:

```
- [ ] Text starts here at column 7
12345678^ (8 spaces — 2 past where text starts)
```
