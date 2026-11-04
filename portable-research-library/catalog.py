#!/usr/bin/env python3
"""Browse a pinned, local procedure library and optionally link selected skills."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import sys

ROOT = Path(__file__).resolve().parent


def read_catalog():
    return json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))


def local_path(relative):
    path = (ROOT / relative).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Path leaves the library')
    return path


def skill_name(path):
    text = path.read_text(encoding='utf-8')
    if not text.startswith('---'):
        return None
    match = re.search(r'^name:\s*[\"\']?([a-zA-Z0-9_-]+)', text.split('---', 2)[1], re.M)
    return match.group(1) if match else None


def activate(data, profile, project, apply=False, copy=False):
    entries = {item['id']: item for item in data['skills']}
    ids = data['profiles'][profile]['skills']
    chosen = [entries[item] for item in ids]
    target = project.expanduser().resolve() / '.agents' / 'skills'
    existing = {}
    if target.exists():
        for item in target.iterdir():
            if (item / 'SKILL.md').is_file():
                name = skill_name(item / 'SKILL.md')
                if name:
                    existing[name] = item
    actions = []
    selected_names = set()
    for item in chosen:
        if item['name'] in selected_names:
            raise ValueError('Profile contains duplicate skill names: ' + item['name'])
        selected_names.add(item['name'])
        source = local_path(item['path']).parent
        name = item['name']
        if not re.fullmatch(r'[a-zA-Z0-9_-]+', name):
            raise ValueError('Invalid skill name: ' + name)
        dest = target / name
        if name in existing or dest.exists() or dest.is_symlink():
            current = existing.get(name, dest)
            if current.is_symlink() and current.resolve() == source:
                actions.append({'skill': name, 'action': 'already-linked', 'path': str(current)})
                continue
            raise ValueError('Existing skill would conflict; no files changed: ' + str(current))
        actions.append({'skill': name, 'action': 'copy' if copy else 'link', 'source': str(source), 'path': str(dest)})
    # All collisions are checked before creating any directories or links.
    if apply:
        target.mkdir(parents=True, exist_ok=True)
        for action in actions:
            if action['action'] == 'already-linked':
                continue
            source, dest = Path(action['source']), Path(action['path'])
            if copy:
                shutil.copytree(source, dest)
                item = next(x for x in chosen if x['name'] == action['skill'])
                license_path = local_path(item['license_path'])
                extra_license = dest / 'UPSTREAM_LICENSE.txt'
                if not extra_license.exists():
                    shutil.copy2(license_path, extra_license)
                (dest / 'UPSTREAM_SOURCE.json').write_text(json.dumps({
                    'id': item['id'], 'url': item['source_url'], 'commit': item['commit'],
                    'sha256': item['sha256'], 'license': item['license']
                }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
            else:
                dest.symlink_to(source, target_is_directory=True)
    return {'applied': apply, 'project': str(project.expanduser().resolve()), 'actions': actions}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    search = sub.add_parser('search')
    search.add_argument('query')
    search.add_argument('--limit', type=int, default=5)
    search.add_argument('--profile')
    show = sub.add_parser('show')
    show.add_argument('id')
    show.add_argument('--text', action='store_true')
    sub.add_parser('profiles')
    sub.add_parser('verify')
    install = sub.add_parser('activate')
    install.add_argument('--profile', required=True)
    install.add_argument('--project', type=Path, required=True)
    install.add_argument('--apply', action='store_true')
    install.add_argument('--copy', action='store_true', help='Copy instead of symlink, for Windows')
    args = parser.parse_args(argv)
    try:
        data = read_catalog()
        if args.command == 'profiles':
            print(json.dumps(data['profiles'], ensure_ascii=False, indent=2))
        elif args.command == 'search':
            tokens = re.findall(r'[\w-]+', args.query.lower())
            allowed = set(data['profiles'][args.profile]['skills']) if args.profile else None
            scored = []
            for item in data['skills']:
                if allowed is not None and item['id'] not in allowed:
                    continue
                name = item['name'].lower()
                text = (name + ' ' + item['description'] + ' ' + item['path']).lower()
                score = sum(5 if token in name else 1 for token in tokens if token in text)
                if score:
                    scored.append((score, item))
            scored.sort(key=lambda pair: (-pair[0], pair[1]['id']))
            output = [{key: item[key] for key in ['id', 'name', 'description', 'path', 'license', 'flags']}
                      for _, item in scored[:max(1, min(args.limit, 20))]]
            print(json.dumps(output, ensure_ascii=False, indent=2))
        elif args.command == 'show':
            item = next(x for x in data['skills'] if x['id'] == args.id)
            print(local_path(item['path']).read_text(encoding='utf-8') if args.text else json.dumps(item, ensure_ascii=False, indent=2))
        elif args.command == 'activate':
            print(json.dumps(activate(data, args.profile, args.project, args.apply, args.copy), ensure_ascii=False, indent=2))
        elif args.command == 'verify':
            manifest = json.loads((ROOT / 'files.sha256.json').read_text(encoding='utf-8'))
            failures = [relative for relative, expected in manifest.items()
                        if not local_path(relative).is_file() or hashlib.sha256(local_path(relative).read_bytes()).hexdigest() != expected]
            print(json.dumps({'checked': len(manifest), 'failures': failures, 'passed': not failures}, ensure_ascii=False))
            return 1 if failures else 0
    except (OSError, ValueError, KeyError, StopIteration) as exc:
        print('Error: ' + str(exc), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
