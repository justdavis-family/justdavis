# yt-history-sync Design

## Overview

**yt-history-sync** is a Python CLI tool (managed with `uv`) that syncs your YouTube watch history and playlist data to a local directory of markdown files — one file per unique video.

It uses the YouTube Data API v3 with OAuth 2.0 to fetch watch history, video metadata, and playlist membership, then writes/updates local markdown files with YAML frontmatter.

## Data Model

### Frontmatter

```yaml
---
video_id: "dQw4w9WgXcQ"
url: "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
title: "Never Gonna Give You Up"
channel: "Rick Astley"
channel_id: "UCuAXFkgsw1L7xaCfnd5JJOw"
playlists:
  - name: "Favorites"
    id: "PLxxxxxx"
  - name: "Music"
    id: "PLyyyyyy"
watch_history:
  - timestamp: "2025-12-01T14:30:00Z"
  - timestamp: "2026-02-15T09:12:00Z"
changelog:
  - timestamp: "2026-02-20T10:00:00Z"
    event: "title_changed"
    old: "Never Gonna Give You Up (Official Video)"
    new: "Never Gonna Give You Up"
  - timestamp: "2026-02-20T10:00:00Z"
    event: "playlist_added"
    playlist: "Music"
  - timestamp: "2026-01-05T10:00:00Z"
    event: "playlist_removed"
    playlist: "Old Jams"
---
```

### Markdown body

```markdown
# Never Gonna Give You Up

## Description

The official video for "Never Gonna Give You Up" by Rick Astley...
```

### Filename convention

`{video_id}-{slugified-title}.md`

Example: `dQw4w9WgXcQ-never-gonna-give-you-up.md`

If a video's title changes, the file is renamed and a `title_changed` event is logged in the changelog.

### Directory structure

Flat — all files in a single `videos/` subdirectory within the output directory.

## Architecture

### Project structure

```
yt-history-sync/
├── pyproject.toml
├── src/
│   └── yt_history_sync/
│       ├── __init__.py
│       ├── cli.py          # Click CLI, argument parsing
│       ├── auth.py         # OAuth 2.0 flow, token load/save/refresh
│       ├── api.py          # YouTube API client wrapper
│       ├── sync.py         # Core sync orchestration & diffing
│       └── markdown.py     # Read/write markdown files with frontmatter
└── docs/
    └── plans/
```

### Sync flow

When the user runs `yt-history-sync sync`:

1. **Authenticate** — load cached OAuth token from `--token-cache` path, or run the browser-based consent flow on first run using `--credentials` file
2. **Fetch watch history** — pull history entries from the API (video ID + timestamp)
3. **Fetch video metadata** — batch-fetch title, channel, description for all video IDs (API supports up to 50 per request)
4. **Fetch playlists** — pull all user playlists, then fetch the video IDs in each
5. **Load existing files** — read current markdown files from `--output-dir`
6. **Diff & update** — for each video:
   - New video: create file
   - Existing video: append watch timestamp, update playlists, detect title/playlist changes and log to changelog, rename file if title changed
7. **Write files** — write all new/modified markdown files to disk

### Incremental sync

On subsequent runs, the tool only fetches history entries newer than the most recent `watch_history` timestamp across all existing files. Playlist membership is always fully re-fetched since there's no incremental API for that.

Use `--full` to force a complete re-sync.

## CLI Interface

```
yt-history-sync sync \
  --credentials PATH   # Path to Google OAuth client credentials JSON (required)
  --output-dir PATH    # Directory for markdown files (required)
  --token-cache PATH   # Path to cached OAuth token (required)
  [--full]             # Force full re-sync
  [--dry-run]          # Show changes without writing
  [--verbose]          # Verbose logging
```

All three path arguments are required, no implicit defaults.

## Dependencies

- **google-api-python-client** — YouTube Data API v3 client
- **google-auth-oauthlib** — OAuth 2.0 browser-based flow
- **python-frontmatter** — read/write YAML frontmatter in markdown files
- **click** — CLI argument parsing

Python >= 3.12. Runnable via `uvx yt-history-sync sync ...` or `uv pip install .`.

## Error Handling

### API quotas

YouTube Data API v3 default quota: 10,000 units/day. Key costs:

- `activities.list` (watch history): 1 unit per request (50 results per page)
- `videos.list` (metadata batch): 1 unit per request (up to 50 video IDs)
- `playlists.list`: 1 unit per request
- `playlistItems.list`: 1 unit per request (50 items per page)

A typical incremental sync uses 15-30 units. A full initial sync of thousands of videos could use a few hundred. Well within daily limits.

### Error handling strategy

- **Auth failure** — clear message to re-run with valid credentials; expired tokens are automatically refreshed via OAuth refresh tokens
- **Quota exceeded** — log progress, exit with clear message. Next run picks up where it left off since written files serve as checkpoints.
- **Network/API errors** — retry transient failures (429, 5xx) with exponential backoff, up to 3 attempts. Fail hard on 4xx client errors.
- **Partial sync** — files are written as processing completes, so interruptions preserve all progress up to that point

## Playlist tracking

### Available from the API

- Which of the user's playlists each video belongs to (playlist title, ID)
- Current playlist membership on each sync

### Change detection (approximated)

YouTube doesn't expose playlist add/remove events with timestamps. Instead:

- On each sync, snapshot which playlists a video is in
- Diff against previous sync to detect adds and removes
- Log changes with the sync timestamp in the changelog

This builds an accurate changelog going forward, though it can't retroactively capture pre-first-sync changes.

## Not available from YouTube

The following were considered but are not exposed by the YouTube API:

- **Watch completion percentage** — not available
- **Device information** — not available
