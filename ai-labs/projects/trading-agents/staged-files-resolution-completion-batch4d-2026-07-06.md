# Batch 4D-D2 — Index-Only Unstage Completed

Date: 2026-07-06

## Approval

Julius approved:

~~~text
Approve Batch 4D-D index-only unstage for staged files outside scope
~~~

## Commands Executed

Executed from workspace root only:

~~~bash
git restore --staged -- ai-labs/projects/trading-agents/.agent
git restore --staged -- knowledge-base
~~~

No git command was run inside `knowledge-base/`.

## Pre-Unstage Staged Counts

From Batch 4D-D1 audit:

- Total staged paths: `35`
- `.agent/` staged paths: `34`
- `knowledge-base` staged entries: `1`
- Other staged paths: `0`

## Post-Unstage Staged Counts

- Total staged paths: `13`
- `.agent/` staged paths: `0`
- `knowledge-base` staged entries: `0`
- Other staged paths: `13`

## Working Tree Status Sample

The working tree may still show untracked/unstaged local files. This batch only cleaned the staging area.

~~~text
 M .gitignore
 M .hermes/.restart_last_processed.json
 D .hermes/.skills_prompt_snapshot.json
 M .hermes/MEMORY.md
 M .hermes/auth.json
 D .hermes/cache/documents/doc_1ef5d708cb56_message.txt
 D .hermes/cache/documents/doc_310b06b59f2c_news-brief-setup
 M .hermes/cache/model_catalog.json
 D .hermes/cache/screenshots/browser_screenshot_a818e7b2b81d4146a32d144643fcef04.png
 M .hermes/channel_directory.json
 M .hermes/config.yaml
 M .hermes/context_length_cache.yaml
 M .hermes/cron/jobs.json
 M .hermes/gateway.lock
 M .hermes/gateway.pid
 M .hermes/gateway_state.json
 M .hermes/kanban.db
 M .hermes/lsp/node_modules/.package-lock.json
 M .hermes/lsp/package-lock.json
 M .hermes/lsp/package.json
 M .hermes/memories/MEMORY.md
 M .hermes/memories/USER.md
 M .hermes/models_dev_cache.json
 M .hermes/ollama_cloud_models_cache.json
 M .hermes/sessions/20260524_064610_a3fb761e.jsonl
 M .hermes/sessions/session_20260524_064610_a3fb761e.json
 M .hermes/sessions/sessions.json
 M .hermes/skills/.bundled_manifest
 M .hermes/skills/.curator_state
 M .hermes/skills/.usage.json
 D .hermes/skills/apple/apple-notes/SKILL.md
 D .hermes/skills/apple/apple-reminders/SKILL.md
 D .hermes/skills/apple/findmy/SKILL.md
 D .hermes/skills/apple/imessage/SKILL.md
 D .hermes/skills/apple/macos-computer-use/SKILL.md
 D .hermes/skills/autonomous-ai-agents/claude-code/SKILL.md
 D .hermes/skills/autonomous-ai-agents/codex/SKILL.md
 D .hermes/skills/autonomous-ai-agents/feynman/SKILL.md
 D .hermes/skills/autonomous-ai-agents/feynman/references/interactive-only.md
 D .hermes/skills/autonomous-ai-agents/feynman/references/oom-debug.md
 D .hermes/skills/autonomous-ai-agents/feynman/references/pexpect-runner.py
 D .hermes/skills/autonomous-ai-agents/feynman/references/plan-discovery.md
 M .hermes/skills/autonomous-ai-agents/hermes-agent/SKILL.md
 M .hermes/skills/autonomous-ai-agents/hermes-agent/references/mempalace-setup.md
 D .hermes/skills/autonomous-ai-agents/opencode/SKILL.md
 D .hermes/skills/autonomous-ai-agents/opencode/references/open-claude-config.md
 D .hermes/skills/autonomous-ai-agents/opencode/references/open-claude-provider.md
 M .hermes/skills/coin68-writer/SKILL.md
 M .hermes/skills/coin68-writer/references/article-structure.md
 D .hermes/skills/creative/ascii-art/SKILL.md
 M .hermes/skills/creative/ascii-video/SKILL.md
 M .hermes/skills/creative/comfyui/scripts/fetch_logs.py
 M .hermes/skills/creative/comfyui/tests/test_common.py
 M .hermes/skills/creative/comfyui/tests/test_extract_schema.py
 M .hermes/skills/creative/comfyui/tests/test_run_workflow.py
 D .hermes/skills/devops/kanban-orchestrator/SKILL.md
 D .hermes/skills/devops/kanban-worker/SKILL.md
 M .hermes/skills/email/himalaya/SKILL.md
 M .hermes/skills/github/codebase-inspection/SKILL.md
 D .hermes/skills/github/github-auth/SKILL.md
 D .hermes/skills/github/github-auth/scripts/gh-env.sh
 D .hermes/skills/github/github-code-review/SKILL.md
 D .hermes/skills/github/github-code-review/references/review-output-template.md
 D .hermes/skills/github/github-issues/SKILL.md
 D .hermes/skills/github/github-issues/templates/bug-report.md
 D .hermes/skills/github/github-issues/templates/feature-request.md
 D .hermes/skills/github/github-pr-workflow/SKILL.md
 D .hermes/skills/github/github-pr-workflow/references/ci-troubleshooting.md
 D .hermes/skills/github/github-pr-workflow/references/conventional-commits.md
 D .hermes/skills/github/github-pr-workflow/templates/pr-body-bugfix.md
 D .hermes/skills/github/github-pr-workflow/templates/pr-body-feature.md
 D .hermes/skills/github/github-repo-management/SKILL.md
 D .hermes/skills/github/github-repo-management/references/github-api-cheatsheet.md
 M .hermes/skills/media/spotify/SKILL.md
 M .hermes/skills/media/youtube-content/SKILL.md
 M .hermes/skills/note-taking/obsidian/SKILL.md
 M .hermes/skills/productivity/airtable/SKILL.md
 M .hermes/skills/productivity/google-workspace/scripts/google_api.py
 M .hermes/skills/productivity/google-workspace/scripts/gws_bridge.py
 M .hermes/skills/productivity/google-workspace/scripts/setup.py
~~~

## Safety Boundaries

- Delete executed: no
- Revert executed: no
- Commit executed: no
- Push executed: no
- Git inside `knowledge-base/`: no
- Live trading: not executed
- Order placement: not executed
- Simulate-live: not executed
- Runtime/default config changes: not changed
- `.env` files read/printed: none

## Result

`completed_with_remaining_staged_paths`
