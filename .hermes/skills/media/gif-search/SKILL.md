---
name: gif-search
description: "Search/download GIFs from Tenor via curl + jq."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
prerequisites:
  env_vars: [TENOR_API_KEY]
  commands: [curl, jq]
metadata:
  hermes:
    tags: [GIF, Media, Search, Tenor, API]
---

# GIF Search (Tenor API)

Search and download GIFs directly via the Tenor API using curl. No extra tools needed.

## When to use

Useful for finding reaction GIFs, creating visual content, and sending GIFs in chat.

## Setup

Set your Tenor API key in your environment (add to `~/.hermes/.env`):

```bash
TENOR_API_KEY=your_key_here
```

Get a free API key at https://developers.google.com/tenor/guides/quickstart — the Google Cloud Console Tenor API key is free and has generous rate limits.

## Prerequisites

- `curl` and `jq` (both standard on macOS/Linux)
- `TENOR_API_KEY` environment variable

## Search for GIFs

```bash
# Search and get GIF URLs
curl -s "https://tenor.googleapis.com/v2/search?q=thumbs+up&limit=5&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.gif.url'

# Get smaller/preview versions
curl -s "https://tenor.googleapis.com/v2/search?q=nice+work&limit=3&key=${TENOR_API_KEY}" | jq -r '.results[].media_formats.tinygif.url'
```

## Download a GIF

```bash
# Search and download the top result
URL=$(curl -s "https://tenor.googleapis.com/v2/search?q=celebration&limit=1&key=${TENOR_API_KEY}" | jq -r '.results[0].media_formats.gif.url')
curl -sL "$URL" -o celebration.gif
```

## Get Full Metadata

```bash
curl -s "https://tenor.googleapis.com/v2/search?q=cat&limit=3&key=${TENOR_API_KEY}" | jq '.results[] | {title: .title, url: .media_formats.gif.url, preview: .media_formats.tinygif.url, dimensions: .media_formats.gif.dims}'
```

## API Parameters

| Parameter | Description |
|-----------|-------------|
| `q` | Search query (URL-encode spaces as `+`) |
| `limit` | Max results (1-50, default 20) |
| `key` | API key (from `$TENOR_API_KEY` env var) |
| `media_filter` | Filter formats: `gif`, `tinygif`, `mp4`, `tinymp4`, `webm` |
| `contentfilter` | Safety: `off`, `low`, `medium`, `high` |
| `locale` | Language: `en_US`, `es`, `fr`, etc. |

## Available Media Formats

Each result has multiple formats under `.media_formats`:

| Format | Use case |
|--------|----------|
| `gif` | Full quality GIF |
| `tinygif` | Small preview GIF |
| `mp4` | Video version (smaller file size) |
| `tinymp4` | Small preview video |
| `webm` | WebM video |
| `nanogif` | Tiny thumbnail |

## Notes

- URL-encode the query: spaces as `+`, special chars as `%XX`
- For sending in chat, `tinygif` URLs are lighter weight
- GIF URLs can be used directly in markdown: `![alt](url)`

## GIPHY Fallback (no API key needed)

When `TENOR_API_KEY` is not set, use GIPHY's direct CDN as a fallback. No auth required.

### Step 1: Find GIF IDs via browser search

Navigate to `https://giphy.com/search/<query>` and extract GIF IDs from the page links:

```js
// In browser console
const links = [...document.querySelectorAll('a[href*="/gifs/"]')];
links.map(a => {
  const parts = a.href.split('/gifs/')[1]?.split('-');
  return parts?.[parts.length-1];
}).filter(Boolean).slice(0, 15);
```

### Step 2: Download by GIF ID

```bash
# Direct CDN URL — no auth needed
curl -sL "https://media.giphy.com/media/<GIF_ID>/giphy.gif" -o output.gif

# Example: steam locomotive
curl -sL "https://media.giphy.com/media/8F3bK4aq1tCo0TLkf7/giphy.gif" -o train.gif
```

### Pitfalls

- **Don't use `i.giphy.com` domain** — the long-form URLs with Y2lk tokens fail intermittently (406 errors)
- **The `media.giphy.com/media/{id}/giphy.gif` pattern** is the reliable short-form URL
- **Lazy-loaded images**: GIPHY pages use lazy loading — `querySelector('img')` returns empty until you scroll. Use the link-based extraction above instead
- **Browser needed for discovery**: The GIF ID extraction requires a browser to navigate GIPHY search. Once you have IDs, `curl` alone works for download
