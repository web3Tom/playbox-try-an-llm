#!/usr/bin/env bash
# Polestar Playbox bootstrap: scaffold env vars, move off main, install deps.
# Idempotent — safe to re-run on every workspace start.
set -euo pipefail

echo "Initializing your Polestar Playbox workspace..."

# 1. Environment variables
if [ ! -f .env ]; then
  echo "Copying .env.example -> .env (fill in your endpoint + tokens)."
  cp .env.example .env
else
  echo ".env already exists; leaving it untouched."
fi

# 2. Move off main onto a personal sandbox branch
CURRENT_BRANCH="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")"
if [ "$CURRENT_BRANCH" = "main" ] || [ "$CURRENT_BRANCH" = "master" ]; then
  USER_ID="$(git config user.name 2>/dev/null | tr '[:upper:] ' '[:lower:]-' || true)"
  [ -z "$USER_ID" ] && USER_ID="${GITLAB_USER_LOGIN:-playbox-user}"
  NEW_BRANCH="sandbox/${USER_ID}-$(date +%s)"
  echo "Creating personal working branch: ${NEW_BRANCH}"
  git checkout -b "$NEW_BRANCH"
else
  echo "Already on a working branch (${CURRENT_BRANCH}); skipping branch creation."
fi

# 3. Python dependencies (uv-managed — no requirements.txt)
if command -v uv >/dev/null 2>&1; then
  echo "Installing Python dependencies with uv..."
  uv sync
else
  echo "WARNING: uv not found on PATH — install it, then run 'uv sync' manually." >&2
fi

echo "Done. Open PROMPTS.md (PMs) or README.md (developers) to begin."
