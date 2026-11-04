#!/usr/bin/env python3
"""Print a merge-only Goose settings fragment; never change Goose configuration."""
from pathlib import Path
import json
import shutil
import sys


def build_fragment(home: Path, node: str, uv: str) -> str:
    browser_bin = home / '.local/share/goose-research-browser/node_modules/.bin/playwright-mcp'
    if not browser_bin.is_file():
        raise ValueError('Playwright MCP не найден. Сначала выполни шаг 2 README.ru.md.')
    cli = browser_bin.resolve(strict=True)
    node_path = Path(node).absolute()
    uv_path = Path(uv).absolute()
    search_paths = list(dict.fromkeys([
        str(node_path.parent), str(uv_path.parent), str(home / '.local/bin')
    ]))
    scalar = lambda value: json.dumps(value, ensure_ascii=False)
    lines = [
        '# Фрагмент для объединения с существующим config.yaml.',
        '# Не заменяй им настройки провайдера и других extensions.',
        'GOOSE_MAX_TURNS: 30',
        'GOOSE_SUBAGENT_MAX_TURNS: 10',
        'GOOSE_MAX_CONCURRENT_SUBAGENTS: 1',
        'GOOSE_AUTO_COMPACT_THRESHOLD: 0.6',
        'GOOSE_CLI_SHOW_COST: true',
        'GOOSE_DISABLE_SESSION_NAMING: true',
        'GOOSE_MOIM_MESSAGE_TEXT: ' + scalar(
            'При начале и продолжении исследования читай PROJECT_STATE.md в рабочем '
            'каталоге, если он существует. Сохраняй цель, ограничения, проверенные '
            'выводы, неизвестное и следующий шаг; обновляй файл перед завершением.'
        ),
        'GOOSE_SEARCH_PATHS:',
        *['  - ' + scalar(path) for path in search_paths],
        'extensions:',
        '  playwright:',
        '    name: playwright',
        '    enabled: true',
        '    type: stdio',
        '    cmd: ' + scalar(str(node_path)),
        '    args:',
        '      - ' + scalar(str(cli)),
        '      - --browser',
        '      - firefox',
        '    env_keys: []',
        '    envs: {}',
        '    timeout: 120',
    ]
    return '\n'.join(lines) + '\n'


def main() -> int:
    node, uv = shutil.which('node'), shutil.which('uv')
    if not node or not uv:
        print('Нужны node и uv в PATH текущего терминала. См. шаги 2–3 README.ru.md.', file=sys.stderr)
        return 1
    try:
        fragment = build_fragment(Path.home(), node, uv)
    except (ValueError, OSError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    sys.stdout.write(fragment)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
