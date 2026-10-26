#!/usr/bin/env bash
# Translates the next batch of untranslated blog articles through the local router
# (no Google AI Studio cost), validates the site, then commits and pushes to main.
# Run by blog-translation-backlog.timer every 5 hours; the timer disables itself when
# nothing is left. Usage: run-batch.sh [--dry-run]
set -euo pipefail

BLOG=/home/julius/julius-workspace/ai-labs/projects/personal-blog
HERE=$(cd "$(dirname "$0")" && pwd)
WORKTREE=${WORKTREE:-$HOME/.cache/blog-translation-backlog/worktree}
BATCH_SIZE=${BATCH_SIZE:-50}
ROUTER=${ROUTER:-http://127.0.0.1:20128/v1}
# The router serves Gemini under "ag/"; translationModel records the bare name, which CI accepts.
MODEL_PREFIX=${MODEL_PREFIX:-ag/}
MODELS=${MODELS:-gemini-3.8-flash}
# The router runs the model with reasoning on: 30-40 s per article, sometimes over the 90 s default.
TIMEOUT_MS=${TIMEOUT_MS:-300000}
TIMER=blog-translation-backlog.timer
DRY_RUN=0
[ "${1:-}" = "--dry-run" ] && DRY_RUN=1

mkdir -p "$HERE/logs"
exec 9>"$HERE/logs/.lock"
flock -n 9 || { echo "Another batch is still running; skipping."; exit 0; }
LOG="$HERE/logs/$(date +%Y-%m-%d-%H%M).log"
exec > >(tee -a "$LOG") 2>&1
echo "== $(date -Iseconds) batch start (size $BATCH_SIZE, dry run $DRY_RUN)"

fail() { echo "FAILED: $*"; exit 1; }

curl -sf -m 10 "$ROUTER/models" >/dev/null || fail "router $ROUTER is not reachable"

git -C "$BLOG" fetch -q origin
if ! git -C "$WORKTREE" rev-parse --git-dir >/dev/null 2>&1; then
  mkdir -p "$(dirname "$WORKTREE")"
  git -C "$BLOG" worktree add -q --detach "$WORKTREE" origin/main
fi
# Leftovers mean an earlier batch stopped half way; a person should look before anything is overwritten.
# The node_modules symlink is not matched by the "node_modules/" ignore rule, so leave it out.
CLEAN_SPEC=(-- . ':(exclude)node_modules')
[ -z "$(git -C "$WORKTREE" status --porcelain "${CLEAN_SPEC[@]}")" ] || fail "worktree $WORKTREE has uncommitted changes"
git -C "$WORKTREE" checkout -q --detach origin/main
ln -sfn "$BLOG/node_modules" "$WORKTREE/node_modules"
ln -sfn "$BLOG/.env.local" "$WORKTREE/.env.local"

SLUGS=$(node "$HERE/pending-slugs.mjs" "$WORKTREE" "$BATCH_SIZE")
if [ -z "$SLUGS" ]; then
  echo "Backlog is fully translated; disabling $TIMER."
  [ "$DRY_RUN" = 1 ] || systemctl --user disable --now "$TIMER" || true
  exit 0
fi
COUNT=$(tr ',' '\n' <<<"$SLUGS" | wc -l)
REMAINING=$(node "$HERE/pending-slugs.mjs" "$WORKTREE" 100000 | tr ',' '\n' | grep -c . || true)
echo "Pending: $REMAINING; this batch: $COUNT"
echo "$SLUGS" | tr ',' '\n'
[ "$DRY_RUN" = 1 ] && { echo "Dry run: nothing translated."; exit 0; }

# Exported values win over .env.local, so this run can never fall back to the paid Gemini API.
set +e
(cd "$WORKTREE" && env \
  TRANSLATION_OPENAI_BASE_URL="$ROUTER" \
  TRANSLATION_OPENAI_MODEL_PREFIX="$MODEL_PREFIX" \
  GEMINI_MODELS="$MODELS" \
  GEMINI_TRANSLATION_BATCH_SIZE="$COUNT" \
  GEMINI_TRANSLATION_TIMEOUT_MS="$TIMEOUT_MS" \
  node --env-file-if-exists=.env.local scripts/translate-content.mjs --slugs "$SLUGS")
TRANSLATE_STATUS=$?
set -e
[ "$TRANSLATE_STATUS" = 0 ] || echo "Some articles failed; they stay pending for the next batch."

mapfile -t CHANGED < <(git -C "$WORKTREE" status --porcelain --untracked-files=all "${CLEAN_SPEC[@]}" | sed 's/^...//')
[ "${#CHANGED[@]}" -gt 0 ] || fail "no article was translated"
for path in "${CHANGED[@]}"; do
  slug=$(basename "$path" .md)
  [[ "$path" == src/content/translations/en/*.md && ",$SLUGS," == *",$slug,"* ]] || fail "unexpected change: $path"
done

if ! (cd "$WORKTREE" && npx vitest run && npm run build >"$HERE/logs/build-last.log" 2>&1); then
  # Park the batch so the worktree is clean for the next run; nothing is deleted.
  PARKED="$HERE/logs/failed-$(date +%Y%m%d-%H%M)"
  mkdir -p "$PARKED"
  for path in "${CHANGED[@]}"; do mv "$WORKTREE/$path" "$PARKED/"; done
  fail "tests or build failed; translations parked in $PARKED (see logs/build-last.log)"
fi

git -C "$WORKTREE" add -- "${CHANGED[@]}"
git -C "$WORKTREE" commit -q -m "content(en): translate ${#CHANGED[@]} backlog articles via local router"
for attempt in 1 2 3; do
  if git -C "$WORKTREE" push -q origin HEAD:main; then
    echo "Pushed $(git -C "$WORKTREE" rev-parse --short HEAD) with ${#CHANGED[@]} translations."
    exit 0
  fi
  echo "Push rejected (attempt $attempt); rebasing onto the new main."
  git -C "$WORKTREE" fetch -q origin
  git -C "$WORKTREE" rebase -q origin/main || { git -C "$WORKTREE" rebase --abort; fail "rebase conflict; commit left in $WORKTREE"; }
done
fail "push failed three times; commit left in $WORKTREE"
