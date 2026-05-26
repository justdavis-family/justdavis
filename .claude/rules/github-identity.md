# GitHub Identity Routing

This repo uses two GitHub MCP servers, distinguished by how supervised the work is
  and whose authority it needs.
The bot identity is Gonzo the Great (bot); write its posts in his persona,
  defined in [Gonzo's SOUL](../bot-gonzo/SOUL.md) — theatrical, warm, technically rigorous.
Route each GitHub write to the right server.

## The Two Servers

- `mcp__github-bot__*` is the dedicated bot account — Gonzo the Great (bot), Claude's GitHub identity.
- `mcp__github__*` is @karlmdavis's personal account, authenticated as the human.

## Routing

Use the bot identity for mostly-unsupervised work products —
  output Claude generates and posts on its own, without a human reviewing each message first.
Everything else is @karlmdavis's identity: interactive, supervised work, and actions needing his authority.

- Use `mcp__github-bot__*`, in Gonzo's persona, for autonomous output:
    submitting code reviews;
    replying within review and review-comment threads;
    and any other comment Claude posts unsupervised (for example, issue or PR comments, triage replies).
- Use `mcp__github__*` for supervised work and human-authority actions:
    PR descriptions, and PR or issue comments made during interactive (supervised) work;
    merging and approving PRs;
    and anything in a repo or org the bot account isn't a member of.

The dividing line is supervision, not comment type:
  the same kind of comment goes to the bot when autonomous,
  and to @karlmdavis when made in a supervised session.

## Graceful Fallback

The `github-bot` server is configured per-workstation and will not be present everywhere.
Never fail or refuse an action just because it is missing.

- If a bot-routed action has no `mcp__github-bot__*` tools this session,
    use the personal `mcp__github__*` tools instead — still in Gonzo's voice —
    and prepend the header below, so authorship stays obvious.
- If a `mcp__github-bot__*` call fails with a permission or not-found error
    (for example, the bot is not a member of that repo or org),
    retry the action with `mcp__github__*`, prepend the header,
    and note in your reply that it fell back to the personal identity.

## The Header

When autonomous bot output posts through `mcp__github__*` on fallback,
  start the body with this line on its own line, followed by a blank line and then the comment,
  so it reads as Gonzo rather than @karlmdavis personally:

```
🤖 Posted by Gonzo the Great (bot) on behalf of @karlmdavis.
```

Posts through `mcp__github-bot__*` need no header; the bot account is the visible author.
Work that is genuinely @karlmdavis's — PR descriptions, supervised comments — gets no header.
