#!/usr/bin/env bash
# =============================================================================
# Workspace Skeleton Generator v2.0
# Tạo toàn bộ folder structure + placeholder files
# Chạy từ thư mục root của workspace repo
# =============================================================================

set -e  # Dừng ngay khi có lỗi

echo "🏗️  Bắt đầu tạo skeleton workspace..."
echo ""

# -----------------------------------------------------------------------------
# Hàm helper: tạo folder + .gitkeep nếu folder rỗng
# -----------------------------------------------------------------------------
mkdir_with_keep() {
  mkdir -p "$1"
  touch "$1/.gitkeep"
}

# Hàm tạo file rỗng (chỉ tạo nếu chưa tồn tại)
touch_if_missing() {
  if [ ! -f "$1" ]; then
    touch "$1"
    echo "  📄 $1"
  fi
}

# =============================================================================
# 1. ROOT FILES
# =============================================================================
echo "📦 [1/7] Tạo root files..."
touch_if_missing "AGENTS.md"
touch_if_missing "README.md"
touch_if_missing ".gitignore"
touch_if_missing ".gitmodules"

# =============================================================================
# 2. LEARNING/
# =============================================================================
echo "📦 [2/7] Tạo learning/..."
mkdir -p learning/python/oop/knowledge
mkdir -p learning/python/oop/practice
mkdir_with_keep learning/python/file-io
mkdir_with_keep learning/python/git-github
mkdir_with_keep learning/prompt-engineering
mkdir_with_keep learning/good-taste-writing

touch_if_missing "learning/python/oop/knowledge/what-is-oop.md"
touch_if_missing "learning/python/oop/practice/oop-1.py"
touch_if_missing "learning/python/oop/practice/oop-2.py"

# =============================================================================
# 3. WORKING/
# =============================================================================
echo "📦 [3/7] Tạo working/..."

# Clients
mkdir -p working/clients/client-1/contents
mkdir -p working/clients/client-1/images
mkdir -p working/clients/client-2/contents
mkdir -p working/clients/client-2/images

touch_if_missing "working/clients/AGENTS.md"
touch_if_missing "working/clients/clients.md"
touch_if_missing "working/clients/client-1/client-1.md"
touch_if_missing "working/clients/client-2/client-2.md"

# Substack (PascalCase - brand exception)
mkdir -p working/Substack/content
mkdir -p working/Substack/images

touch_if_missing "working/Substack/AGENTS.md"
touch_if_missing "working/Substack/content/content.md"

# X (PascalCase - brand exception)
mkdir -p working/X/content
mkdir -p working/X/images/post-1
mkdir -p working/X/images/thread-1
mkdir -p working/X/images/article-1

touch_if_missing "working/X/AGENTS.md"
touch_if_missing "working/X/content/posts.md"
touch_if_missing "working/X/content/threads.md"
touch_if_missing "working/X/content/articles.md"

# Coin68 (PascalCase - brand exception)
mkdir -p working/Coin68/context
mkdir -p working/Coin68/content/drafts
mkdir -p working/Coin68/content/published
mkdir -p working/Coin68/assets/templates
mkdir -p working/Coin68/assets/projects-images

touch_if_missing "working/Coin68/coin68.md"
touch_if_missing "working/Coin68/AGENTS.md"
touch_if_missing "working/Coin68/context/context.md"
touch_if_missing "working/Coin68/context/julius.md"
touch_if_missing "working/Coin68/context/coin68.md"
touch_if_missing "working/Coin68/content/published/published.md"
touch_if_missing "working/Coin68/content/published/layer-1.md"
touch_if_missing "working/Coin68/content/published/layer-2.md"

# =============================================================================
# 4. AI-LABS/
# =============================================================================
echo "📦 [4/7] Tạo ai-labs/..."

# Projects (template cho 1 project)
mkdir -p ai-labs/projects/project-1/context
mkdir -p ai-labs/projects/project-1/skills/skill-1
mkdir -p ai-labs/projects/project-1/skills/skill-2
mkdir -p ai-labs/projects/project-1/agents
mkdir -p ai-labs/projects/project-1/tools/mcp
mkdir -p ai-labs/projects/project-1/tools/plugin
mkdir -p ai-labs/projects/project-1/src/api
mkdir -p ai-labs/projects/project-1/src/code
mkdir -p ai-labs/projects/project-1/src/module

touch_if_missing "ai-labs/projects/project-1/project-1.md"
touch_if_missing "ai-labs/projects/project-1/README.md"
touch_if_missing "ai-labs/projects/project-1/AGENTS.md"
touch_if_missing "ai-labs/projects/project-1/CLAUDE.md"
touch_if_missing "ai-labs/projects/project-1/context/architecture.md"
touch_if_missing "ai-labs/projects/project-1/context/idea.md"
touch_if_missing "ai-labs/projects/project-1/context/doc.md"
touch_if_missing "ai-labs/projects/project-1/skills/skill-1/SKILL.md"
touch_if_missing "ai-labs/projects/project-1/skills/skill-2/SKILL.md"
touch_if_missing "ai-labs/projects/project-1/agents/agent-1.md"
touch_if_missing "ai-labs/projects/project-1/agents/agent-2.md"

# Đảm bảo các sub-folder rỗng được giữ
[ ! "$(ls -A ai-labs/projects/project-1/tools/mcp 2>/dev/null)" ] && touch ai-labs/projects/project-1/tools/mcp/.gitkeep
[ ! "$(ls -A ai-labs/projects/project-1/tools/plugin 2>/dev/null)" ] && touch ai-labs/projects/project-1/tools/plugin/.gitkeep
[ ! "$(ls -A ai-labs/projects/project-1/src/api 2>/dev/null)" ] && touch ai-labs/projects/project-1/src/api/.gitkeep
[ ! "$(ls -A ai-labs/projects/project-1/src/code 2>/dev/null)" ] && touch ai-labs/projects/project-1/src/code/.gitkeep
[ ! "$(ls -A ai-labs/projects/project-1/src/module 2>/dev/null)" ] && touch ai-labs/projects/project-1/src/module/.gitkeep

# Systems
mkdir -p ai-labs/systems/llm-knowledge-base
mkdir_with_keep ai-labs/systems/system-2

touch_if_missing "ai-labs/systems/systems.md"
touch_if_missing "ai-labs/systems/llm-knowledge-base/llm-knowledge-base.md"
touch_if_missing "ai-labs/systems/llm-knowledge-base/litepaper.md"
touch_if_missing "ai-labs/systems/llm-knowledge-base/setup-guide.md"

# Workflows
mkdir -p ai-labs/workflows
touch_if_missing "ai-labs/workflows/workflows.md"

# Pipelines
mkdir -p ai-labs/pipelines
touch_if_missing "ai-labs/pipelines/pipelines.md"

# Resource
mkdir -p ai-labs/resource/api-keys
mkdir -p ai-labs/resource/plugins
mkdir -p ai-labs/resource/mcps
mkdir -p ai-labs/resource/prompts
mkdir -p ai-labs/resource/personas
mkdir -p ai-labs/resource/skills/thread-writer
mkdir -p ai-labs/resource/skills/article-writer
mkdir -p ai-labs/resource/skills/substack-writer
mkdir -p ai-labs/resource/skills/seo-optimizer
mkdir -p ai-labs/resource/skills/researcher

touch_if_missing "ai-labs/resource/api-keys/.env.example"
touch_if_missing "ai-labs/resource/api-keys/.env"
touch_if_missing "ai-labs/resource/api-keys/README.md"
touch_if_missing "ai-labs/resource/plugins/plugins.md"
touch_if_missing "ai-labs/resource/mcps/mcps.md"
touch_if_missing "ai-labs/resource/prompts/prompts.md"
touch_if_missing "ai-labs/resource/personas/personas.md"
touch_if_missing "ai-labs/resource/skills/skills.md"
touch_if_missing "ai-labs/resource/skills/thread-writer/SKILL.md"
touch_if_missing "ai-labs/resource/skills/article-writer/SKILL.md"
touch_if_missing "ai-labs/resource/skills/substack-writer/SKILL.md"
touch_if_missing "ai-labs/resource/skills/seo-optimizer/SKILL.md"
touch_if_missing "ai-labs/resource/skills/researcher/SKILL.md"

# =============================================================================
# 5. KNOWLEDGE-BASE/  (SUBMODULE - bỏ qua nếu đã tồn tại)
# =============================================================================
echo "📦 [5/7] Kiểm tra knowledge-base submodule..."

if [ -d "knowledge-base/.git" ] || [ -f "knowledge-base/.git" ]; then
  echo "  ✅ knowledge-base submodule đã tồn tại, bỏ qua."
else
  echo "  ⚠️  knowledge-base chưa được add làm submodule."
  echo "     Chạy lệnh sau SAU khi script này xong:"
  echo "     git submodule add git@github.com:juliuss1907/knowledge-base.git knowledge-base"
fi

# =============================================================================
# 6. TASKS/
# =============================================================================
echo "📦 [6/7] Tạo tasks/..."

mkdir -p tasks/scheduled
mkdir -p tasks/processing
mkdir -p tasks/approved

touch_if_missing "tasks/TASK_TEMPLATE.md"
touch_if_missing "tasks/TASK_SKILL.md"
touch_if_missing "tasks/tasks.md"
touch_if_missing "tasks/scheduled/scheduled.md"
touch_if_missing "tasks/processing/processing.md"
touch_if_missing "tasks/approved/approved.md"

# =============================================================================
# 7. BACKUPS/  (không commit, chỉ tạo folder local)
# =============================================================================
echo "📦 [7/7] Tạo backups/ (local only, không commit)..."

mkdir -p backups/chrome
mkdir -p backups/msty-studio

# =============================================================================
# DONE
# =============================================================================
echo ""
echo "✅ Skeleton đã được tạo xong!"
echo ""
echo "📋 Bước tiếp theo:"
echo "   1. Add knowledge-base làm submodule (nếu chưa):"
echo "      git submodule add git@github.com:juliuss1907/knowledge-base.git knowledge-base"
echo ""
echo "   2. Cấu hình submodule auto-update khi clone:"
echo "      git config -f .gitmodules submodule.knowledge-base.update merge"
echo ""
echo "   3. Review .gitignore và edit nếu cần."
echo ""
echo "   4. Commit lần đầu:"
echo "      git add ."
echo "      git commit -m 'init: workspace skeleton v2.0'"
echo "      git push origin main"
