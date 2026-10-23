# Reading X posts with twitter-cli — 2026-09-29 session

Companion to `references/x-content-extraction.md` (which holds the failed-path
table and the RSS fallback). This file records what changed on 2026-09-29 when
a three-link batch of x.com URLs all reported "no content extracted".

## A "no content extracted" warning is not a dead end

The desktop reader hit X's login wall on all three links:
`@claudeai/2104633115620823187`, `@IceSolst/2104701177141264485`,
`@drfeifei/2104664403681632453`. All three read fine with one
`twitter tweet <ID>` call each. Do not skip a story, and do not fall through to
RSS, because the task description shows a Context Warning.

## Exact commands that worked

```bash
twitter tweet 2104633115620823187              # YAML
twitter tweet 2104633115620823187 --full-text  # flag is --full-text, NOT --full
agent-reach doctor                              # confirms twitter-cli is wired
```

Every call prints a benign `WARNING twitter_cli.client: Failed to init
ClientTransaction: 'NoneType' object has no attribute 'group'` on stderr. The
YAML on stdout is complete. Ignore it or redirect with `2>/dev/null`.

`agent-reach` itself only has setup/install/doctor subcommands. `doctor` is the
useful one; there is no `agent-reach read <url>`.

## The default output is a thread, not just a tweet

`twitter tweet <ID>` returns a YAML `data:` list. Entry 0 is the tweet; later
entries are the thread, the **quoted tweet** (nested under `quotedTweet` with
the same shape), and notable replies with their own metrics.

This is what made the Anthropic photo-credit story verifiable in three calls:
- the complaint (`@IceSolst`) plus its nested quoted ClaudeDevs post,
- `@IceSolst` pointing at the photo's original post,
- `@RLanceMartin` apologizing ("It was a miss to not credit you in the blog
  post ... I'm really sorry about this!") and confirming credit was added.

Compact `-c` mode truncates text. Use the default when quoting.

## X Articles come back inline in `articleText`

A tweet whose `urls:` include `x.com/i/article/<id>` carries `articleTitle:`
and a long `articleText:` field on the main entry. No fxtwitter/curl detour
needed.

Fei-Fei Li's "To Seek a Newer World" (id `2104664403681632453`) came back as a
full multi-section essay, including the "Following our North Star to AMD"
section with her reasoning about needing to get closer to hardware. To read
the tail without dumping the whole thread:

```bash
twitter tweet 2104664403681632453 2>/dev/null | sed -n '/articleText/,$p'
```

The curl-to-fxtwitter variant still works but requires a separate fetch and
was unnecessary here.

## Keep a resolved incident in proportion

The photo-credit complaint closed inside hours: apology posted, credit added to
the blog post. The article covered it in a short section, stated the resolution
in the same paragraph, and did not make the launch story a controversy piece.
When a minor complaint is already resolved, say so and keep it as a footnote
rather than escalating it.

## Pipeline note

`twitter tweet <ID> | python3 -c "..."` trips the security scanner
("curl | python3" pattern) and needs auto-approval. It works, but for plain
reading just run `twitter tweet <ID>` and read the YAML directly, or redirect
to a file and use `sed` / `read_file` instead of piping into an interpreter.
