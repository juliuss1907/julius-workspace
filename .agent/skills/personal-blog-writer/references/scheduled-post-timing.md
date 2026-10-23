# Scheduled post timing

When turning a brief into scheduled blog drafts, calculate `scheduledAt` only after the drafts are complete. Writing, source checks, build validation, staging, and pushing can consume the original 30-minute buffer.

Before the final build, recalculate the first UTC timestamp as the current completion time plus 30 minutes. Keep the remaining posts exactly two hours apart. Then verify the committed remote frontmatter contains the recalculated ISO timestamps and `draft: true`.
