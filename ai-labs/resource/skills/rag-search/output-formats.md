# Output Format Templates

## Direct Answer (1 source)

```
[Answer in 1-3 sentences]

Source: [[path/to/file.md]] — [brief context]
```

---

## Synthesized Answer (multiple sources)

```
[2-3 sentence synthesis]

Sources:
- [[source-1.md]] — [what it contributes]
- [[source-2.md]] — [what it contributes]
```

---

## Exploratory Answer

```
**[Concept Name]**
[2-3 sentence summary]

**Related:**
- [[concept-1]] — [how it relates]
- [[concept-2]] — [how it relates]

**Sources:**
- [[source-1]]
- [[source-2]]
```

---

## Not Found

```
I didn't find anything about [topic] in the knowledge-base or workspace.

Suggestions:
- If you've read about this, it might be in raw/ but not yet compiled
- If it's new, consider adding it via OpenClaw ingest
- If it's in personal/, I can't access it (workspace rule)
```

---

## Conflicting Information

```
I found conflicting information:

**Source 1** ([[path/to/file1.md]]):
[explanation 1]

**Source 2** ([[path/to/file2.md]]):
[explanation 2]

These conflict on [specific point]. Which is correct, or should I flag this for KB cleanup?
```
