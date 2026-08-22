# GitHub Identity Routing

This repo uses two GitHub identity channels, distinguished by how supervised the work is
  and whose authority it needs.
The bot identity is Gonzo the Great (bot); write its posts in his persona,
  defined in [Gonzo's SOUL](../bot-gonzo/SOUL.md) — theatrical, warm, technically rigorous.
Route each GitHub write to the right channel.

## The Two Channels

- `mcp__claude_ai_GitHub_MCP__*` is the dedicated bot account — Gonzo the Great (bot),
    Claude's GitHub identity, served by the claude.ai GitHub MCP integration.
- The `gh` CLI under @karlmdavis's auth is the human channel,
    used for actions that must be attributed to or authorized as @karlmdavis.

## Routing

Use the bot identity for mostly-unsupervised work products —
  output Claude generates and posts on its own, without a human reviewing each message first.
Everything else is @karlmdavis's identity:
  interactive, supervised work, and actions needing his authority.

- Use `mcp__claude_ai_GitHub_MCP__*`, in Gonzo's persona, for autonomous output:
    submitting code reviews;
    replying within review and review-comment threads;
    and any other comment Claude posts unsupervised (for example, issue or PR comments, triage replies).
- Use the `gh` CLI for supervised work and human-authority actions:
    PR descriptions, and PR or issue comments made during interactive (supervised) work;
    merging and approving PRs;
    and anything in a repo or org the bot account isn't a member of.

The dividing line is supervision, not comment type:
  the same kind of comment goes to the bot when autonomous,
  and to @karlmdavis when made in a supervised session.
Acting on webhook-driven PR events without per-step approval is autonomous output,
  even when @karlmdavis is reachable in the same session.

## Graceful Fallback

The bot's MCP server is reached via the claude.ai integration,
  which will not be present on every workstation.
Never fail or refuse an action just because it is missing.

- If a bot-routed action has no `mcp__claude_ai_GitHub_MCP__*` tools this session,
    use the `gh` CLI instead — still in Gonzo's voice —
    and prepend the header below, so authorship stays obvious.
- If a `mcp__claude_ai_GitHub_MCP__*` call fails with a permission or not-found error
    (for example, the bot is not a member of that repo or org),
    retry the action with `gh`, prepend the header,
    and note in your reply that it fell back to the personal identity.

## The Header

When autonomous bot output posts through `gh` on fallback,
  start the body with this line on its own line, followed by a blank line and then the comment,
  so it reads as Gonzo rather than @karlmdavis personally:

```
🤖 Posted by Gonzo the Great (bot) on behalf of @karlmdavis.
```

Posts through `mcp__claude_ai_GitHub_MCP__*` need no header; the bot account is the visible author.
Work that is genuinely @karlmdavis's — PR descriptions, supervised comments — gets no header.
