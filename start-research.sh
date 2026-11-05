#!/usr/bin/env bash
set -euo pipefail

research_project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$research_project_dir"
export PATH="$HOME/.local/bin:$PATH"

if ! command -v goose >/dev/null 2>&1; then
  printf '%s\n' 'Goose CLI not found. Install Goose first: see README.md.' >&2
  exit 1
fi

export GOOSE_MOIM_MESSAGE_FILE="$research_project_dir/PROJECT_STATE.md"
export GOOSE_MAX_TURNS=30
export GOOSE_SUBAGENT_MAX_TURNS=10
export GOOSE_MAX_CONCURRENT_SUBAGENTS=1
export GOOSE_AUTO_COMPACT_THRESHOLD=0.6
export GOOSE_CLI_SHOW_COST=true
export GOOSE_DISABLE_SESSION_NAMING=true

exec goose session --max-turns 30 --max-tool-repetitions 3 "$@"
