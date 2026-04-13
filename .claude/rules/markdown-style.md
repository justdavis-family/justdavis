# Markdown Style

All markdown files follow standardized formatting rules.
These rules are intended to strike a balance
  where content is easy to read and edit in code editors
  and where `diff` output for long sections of prose is cleaner.

## Headers and Sections

Every header should have one blank line above it,
  except for headers at the start of a file,
  which should not have any blank lines above them.

There should never be more than one blank line before or after headers;
  normalize multiple line breaks right before and after headers
  to a single blank line.

## Line Structure

- One sentence per line for better version control.
- 110-character line wrap limit at natural breakpoints,
    such as after punctuation like commas, colons, semicolons,
    and also at the start of new clauses/sentence parts.
  - Lines _can_ optionally be wrapped more aggressively than that at natural breakpoints,
      even when not needed to avoid exceeding the length limit,
      but care should be taken to try and balance out
      the length of the lines in each block/paragraph.
- Meet the line length limit with whitespace changes only
    (line breaks and continuation indentation);
    never alter content to shorten a line.
- Some elements will consistently exceed the limit and that's fine,
    e.g., URLs, Markdown links, Markdown table rows,
    and reference-style link definitions.
- Always use POSIX line endings.
- Remove trailing whitespace, except where required by Markdown.
- Always end files with a trailing newline.

## Continuation Indentation

All sentences within a block should start at the same column.
All lines wrapped _within_ a sentence
  should be indented 2 spaces past the sentence start's column.
List item and task checkbox decorations set the sentence start column:
  sentences start one space past the end of the decoration.
Continuation lines within those sentences follow the same rule as all sentences:
  they should be indented 2 spaces past the sentence start's column.

## Punctuation

End all sentence-like lines with periods, including:

- Regular prose sentences.
- List items (bullet points and numbered lists).
- Checklist items (todo entries).
- Table cells containing full sentences.
- Code comments in markdown code blocks (follow language conventions).

## Examples

Wrapping regular prose (2 spaces):

```markdown
Lorem ipsum dolor sit amet, consectetur adipiscing elit,
  sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.
Excepteur sint occaecat cupidatat non proident,
  sunt in culpa qui officia deserunt mollit anim id est laborum.
```

Wrapping sentences in list items:

```markdown
- Lorem ipsum dolor sit amet, consectetur adipiscing elit,
    sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
  Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.
```

Wrapping sentences in checklist items:

```markdown
- [ ] Lorem ipsum dolor sit amet, consectetur adipiscing elit,
        sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.
      Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi
        ut aliquip ex ea commodo consequat.
```

Visual guide for checklist indentation within a sentence:

```
- [ ] Text starts here at column 7,
        and at column 9, here.
        ^
        8 spaces before the start of the wrapped line; 2 past the start of its sentence.
```
