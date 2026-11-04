#!/usr/bin/env bash
set -euo pipefail

if ! command -v python3 >/dev/null 2>&1 || ! python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then
    printf '%s\n' 'Для установки нужен Python 3.10+.' >&2
    exit 1
fi

repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$repo_dir/install.py" "$@"
