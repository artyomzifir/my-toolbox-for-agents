"""Install Goose and the R&D kit for the current Linux user."""

import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import urllib.request


ROOT = Path(__file__).resolve().parent
BEGIN = '# BEGIN Goose R&D Kit'
END = '# END Goose R&D Kit'
LEGACY_BLOCKS = (('# BEGIN Goose Research Kit', '# END Goose Research Kit'),)
PROFILES = ('research-core', 'ml-core', 'software-core')
RETIRED_SKILLS = ('production-engineering', 'writing-plans', 'testing-strategy', 'system-design',
                  'investigate-first', 'verify-and-stop')
PAYLOAD = ('.goosehints', 'production-rules.md', 'document-tools.toml', 'portable-research-library')
GOOSE_RELEASES = 'https://github.com/aaif-goose/goose/releases'
PLAYWRIGHT_VERSION = '0.0.84'

sys.path.insert(0, str(ROOT / '_vendor'))
import yaml


def run(args, *, env=None, quiet=False):
    return subprocess.run(
        [str(arg) for arg in args], check=True, env=env, stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE if quiet else None, text=True,
    )


def download(url, path):
    request = urllib.request.Request(url, headers={'User-Agent': 'goose-research-kit'})
    with urllib.request.urlopen(request, timeout=60) as source, path.open('wb') as target:
        shutil.copyfileobj(source, target)


def sha256(path):
    digest = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def executable(name, local_bin):
    path = shutil.which(name)
    if path:
        return Path(path).absolute()
    candidate = local_bin / name
    return candidate if candidate.is_file() and os.access(candidate, os.X_OK) else None


def run_installer(url, shell, temporary, variables):
    path = temporary / 'upstream-install.sh'
    download(url, path)
    run([shell, path], env={**os.environ, **variables})


def node_environment(node):
    return {**os.environ, 'PATH': str(node.parent) + os.pathsep + os.environ.get('PATH', '')}


def get_node(data, temporary, local_bin):
    managed = data / 'node' / 'bin' / 'node'
    system = executable('node', local_bin)
    for node in (managed, system):
        if node and node.is_file() and (node.parent / 'npm').is_file():
            version = run([node, '-p', 'process.versions.node.split(".")[0]'], quiet=True)
            if int(version.stdout.strip()) >= 20:
                return node

    arch = {'x86_64': 'x64', 'aarch64': 'arm64'}.get(platform.machine())
    if not arch:
        raise RuntimeError('This architecture needs Node.js 20+ with npm installed.')
    print('Installing Node.js for the browser.', flush=True)
    releases = 'https://nodejs.org/dist/latest-v24.x/'
    sums = temporary / 'node-sha256.txt'
    download(releases + 'SHASUMS256.txt', sums)
    for line in sums.read_text().splitlines():
        digest, filename = line.split(maxsplit=1)
        if re.fullmatch(rf'node-v24\.\d+\.\d+-linux-{arch}\.tar\.xz', filename):
            break
    else:
        raise RuntimeError('Node.js is missing from the official release list.')
    archive = temporary / filename
    download(releases + filename, archive)
    if sha256(archive) != digest:
        raise RuntimeError('Node.js checksum mismatch.')
    run(['tar', '-xJf', archive, '-C', temporary])
    os.replace(temporary / filename.removesuffix('.tar.xz'), data / 'node')
    return managed


def browser_config(data, temporary, local_bin, existing):
    if isinstance(existing, dict):
        transport = existing.get('type')
        command = existing.get('cmd')
        if transport == 'streamable_http' and existing.get('uri'):
            return {**existing, 'enabled': True}, []
        if transport == 'stdio' and command and executable(command, local_bin):
            args = existing.get('args') or []
            if not args or not args[0].endswith('/cli.js') or Path(args[0]).is_file():
                return {**existing, 'enabled': True}, [str(executable(command, local_bin).parent)]

    node = get_node(data, temporary, local_bin)
    browser = data / 'playwright'
    cli = browser / 'node_modules/@playwright/mcp/cli.js'
    playwright = browser / 'node_modules/playwright'
    ready = browser / '.firefox-ready'
    browser.mkdir(exist_ok=True)
    env = node_environment(node)
    if not cli.is_file() or not (playwright / 'cli.js').is_file():
        print('Installing Playwright MCP.', flush=True)
        run([node.parent / 'npm', 'install', '--prefix', browser, '--no-audit',
             '--no-fund', '--save-exact', f'@playwright/mcp@{PLAYWRIGHT_VERSION}'], env=env)
    if not ready.is_file():
        print('Preparing Firefox for Playwright.', flush=True)
        run([node, playwright / 'cli.js', 'install', 'firefox'], env=env)
        smoke = "require(process.argv[1]).firefox.launch().then(b => b.close()).catch(e => { console.error(e.message); process.exit(1); })"
        try:
            run([node, '-e', smoke, playwright], env=env)
        except subprocess.CalledProcessError:
            run([node, playwright / 'cli.js', 'install', '--with-deps', 'firefox'], env=env)
            run([node, '-e', smoke, playwright], env=env)
        ready.touch()
    return {
        'name': 'playwright', 'enabled': True, 'type': 'stdio', 'cmd': str(node),
        'args': [str(cli), '--browser', 'firefox', '--headless'],
        'env_keys': [], 'envs': {}, 'timeout': 120,
    }, [str(node.parent)]


def write_file(path, text, backup=False):
    path = path.resolve()
    current = path.read_text(encoding='utf-8') if path.is_file() else None
    if current == text:
        return
    if current is not None and backup:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix=path.name + '.before-kit-', delete=False) as previous:
            previous.write(current.encode())
    with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.research-kit-', delete=False) as pending:
        pending.write(text.encode())
    os.replace(pending.name, path)


def read_config(path):
    if not path.exists():
        return {}
    try:
        result = yaml.safe_load(path.read_text(encoding='utf-8'))
    except yaml.YAMLError:
        raise ValueError(f'Check the YAML in {path}. The existing file was kept.') from None
    if result is None:
        return {}
    if not isinstance(result, dict):
        raise ValueError('The root of config.yaml must be a YAML mapping.')
    return result


def merge_settings(config, browser, search_paths):
    extensions = config.setdefault('extensions', {})
    if not isinstance(extensions, dict):
        raise ValueError('The extensions section must be a YAML mapping.')
    for name in ('developer', 'skills', 'todo', 'chatrecall'):
        extension = extensions.setdefault(name, {'name': name, 'type': 'platform', 'bundled': True})
        if not isinstance(extension, dict):
            raise ValueError(f'The {name} extension setting must be a YAML mapping.')
        extension['enabled'] = True
    extensions['playwright'] = browser
    for key, value in {
        'GOOSE_MAX_TURNS': 30,
        'GOOSE_SUBAGENT_MAX_TURNS': 10,
        'GOOSE_MAX_CONCURRENT_SUBAGENTS': 1,
        'GOOSE_AUTO_COMPACT_THRESHOLD': 0.6,
        'GOOSE_CLI_SHOW_COST': True,
        'GOOSE_DISABLE_SESSION_NAMING': True,
    }.items():
        config.setdefault(key, value)
    previous_paths = config.get('GOOSE_SEARCH_PATHS') or []
    if not isinstance(previous_paths, list):
        raise ValueError('GOOSE_SEARCH_PATHS must be a list.')
    config['GOOSE_SEARCH_PATHS'] = list(dict.fromkeys([*previous_paths, *search_paths]))


def link_skills(library, config_dir, home, data):
    catalog = json.loads((library / 'catalog.json').read_text(encoding='utf-8'))
    indexed = {item['id']: item for item in catalog['skills']}
    target = config_dir / 'skills'
    target.mkdir(exist_ok=True)
    sources = {}
    for profile in PROFILES:
        for identifier in catalog['profiles'][profile]['skills']:
            item = indexed[identifier]
            sources.setdefault(item['name'], (library / item['path']).parent)
    for name, source in sources.items():
        link = target / name
        if link.is_symlink() and link.resolve().is_relative_to(data):
            if link.resolve() != source:
                with tempfile.TemporaryDirectory(dir=target) as directory:
                    replacement = Path(directory) / name
                    replacement.symlink_to(source, target_is_directory=True)
                    os.replace(replacement, link)
        elif not link.exists() and not link.is_symlink() and not (home / '.agents/skills' / name / 'SKILL.md').is_file():
            link.symlink_to(source, target_is_directory=True)
    return sources.keys()


def install_user_rules(kit, config_dir, uv, documents):
    hints = config_dir / '.goosehints'
    current = hints.read_text(encoding='utf-8') if hints.exists() else ''
    for old_begin, old_end in LEGACY_BLOCKS:
        legacy = re.compile(rf'(?ms)^{re.escape(old_begin)}\n.*?^{re.escape(old_end)}\n?')
        current = legacy.sub('', current)
    catalogue = shlex.quote(str(kit / 'portable-research-library/catalog.py'))
    rules = (kit / '.goosehints').read_text(encoding='utf-8').replace(
        'portable-research-library/catalog.py', catalogue)
    caveman = kit / 'portable-research-library/upstream/caveman/skills/caveman/SKILL.md'
    rules = rules.replace('Enable Caveman only on an explicit request.',
                          f'On an explicit Caveman request read `{caveman}`.')
    python_tools = f'{shlex.quote(str(uv))} run --project {shlex.quote(str(documents))}'
    rules = rules.replace('Run project Python tools through `uv run`.',
                          f'For Docling, Word, Excel and charts run `{python_tools}` before the command. For repository code use the project environment.')
    production = (kit / 'production-rules.md').read_text(encoding='utf-8').rstrip()
    block = f'{BEGIN}\n{rules.rstrip()}\n\n{production}\n{END}'
    pattern = re.compile(rf'(?ms)^{re.escape(BEGIN)}\n.*?^{re.escape(END)}$')
    if pattern.search(current):
        combined = pattern.sub(lambda _: block, current, count=1)
    else:
        prefix = current.rstrip('\n') + '\n\n' if current.strip() else ''
        combined = prefix + block + '\n'
    write_file(hints, combined)


def apply_user_settings(kit, config_dir, home, data, uv, documents, browser, paths):
    config_dir.mkdir(parents=True, exist_ok=True)
    path = config_dir / 'config.yaml'
    config = read_config(path)
    merge_settings(config, browser, paths)
    selected = link_skills(kit / 'portable-research-library', config_dir, home, data)
    install_user_rules(kit, config_dir, uv, documents)
    write_file(path, yaml.safe_dump(config, allow_unicode=True, sort_keys=False), backup=True)
    for name in RETIRED_SKILLS:
        link = config_dir / 'skills' / name
        if name not in selected and link.is_symlink() and link.resolve().is_relative_to(data):
            link.unlink()


def install_payload(data, temporary):
    run([sys.executable, ROOT / 'portable-research-library/catalog.py', 'verify'])
    digest = hashlib.sha256()
    for name in PAYLOAD:
        source = ROOT / name
        files = sorted(p for p in source.rglob('*') if p.is_file()) if source.is_dir() else [source]
        for path in files:
            digest.update(path.relative_to(ROOT).as_posix().encode() + b'\0' + bytes.fromhex(sha256(path)))
    kit = data / ('bundle-' + digest.hexdigest()[:12])
    if not kit.is_dir():
        staging = temporary / 'payload'
        staging.mkdir()
        for name in PAYLOAD:
            source = ROOT / name
            if source.is_dir():
                shutil.copytree(source, staging / name)
            else:
                shutil.copy2(source, staging / name)
        os.replace(staging, kit)
    return kit


def install_desktop(temporary):
    status = subprocess.run(['dpkg-query', '-W', '-f=${Status}', 'goose'],
                            capture_output=True, text=True, check=False)
    if status.stdout.strip() == 'install ok installed':
        return
    arch = {'x86_64': 'amd64', 'aarch64': 'arm64'}.get(platform.machine())
    if not arch:
        raise RuntimeError('Goose Desktop requires x86_64 or ARM64.')
    metadata = temporary / 'goose-release.json'
    download('https://api.github.com/repos/aaif-goose/goose/releases/latest', metadata)
    assets = json.loads(metadata.read_text(encoding='utf-8'))['assets']
    asset = next((item for item in assets if re.fullmatch(rf'goose_[\w.-]+_{arch}\.deb', item['name'], re.I)), None)
    if not asset or not (asset.get('digest') or '').startswith('sha256:'):
        raise RuntimeError('The latest Goose release has no DEB with a checksum.')
    url = asset['browser_download_url']
    if not url.startswith(GOOSE_RELEASES + '/download/'):
        raise RuntimeError('Unexpected download source for the Goose Desktop package.')
    package = temporary / asset['name']
    print('Installing Goose Desktop. apt may ask for the sudo password.', flush=True)
    download(url, package)
    if 'sha256:' + sha256(package) != asset['digest']:
        raise RuntimeError('Goose Desktop checksum mismatch.')
    subprocess.run(['sudo', 'apt-get', 'install', '-y', str(package)], check=True)


def main(desktop):
    if sys.platform != 'linux' or os.geteuid() == 0:
        raise RuntimeError('Run the installer on Ubuntu as a regular user.')
    home = Path.home()
    local_bin = home / '.local/bin'
    config_home = Path(os.environ.get('XDG_CONFIG_HOME') or home / '.config')
    if not config_home.is_absolute():
        config_home = home / '.config'
    root = Path(os.environ.get('GOOSE_PATH_ROOT') or '.')
    config_dir = root / 'config' if root.is_absolute() else config_home / 'goose'
    data = home / '.local/share/goose-research-kit'
    data.mkdir(parents=True, exist_ok=True)
    with (data / '.install.lock').open('a') as lock, tempfile.TemporaryDirectory(dir=data) as folder:
        fcntl.flock(lock, fcntl.LOCK_EX)
        temporary = Path(folder)
        kit = install_payload(data, temporary)
        config = read_config(config_dir / 'config.yaml')
        extensions = config.get('extensions', {})
        if not isinstance(extensions, dict):
            raise ValueError('The extensions section must be a YAML mapping.')
        goose = executable('goose', local_bin)
        if not goose:
            print('Installing Goose CLI.', flush=True)
            run_installer(GOOSE_RELEASES + '/download/stable/download_cli.sh',
                          'bash', temporary, {'CONFIGURE': 'false', 'GOOSE_BIN_DIR': str(local_bin),
                                             'SHELL': os.environ.get('SHELL') or '/bin/bash'})
            goose = local_bin / 'goose'
        uv = executable('uv', local_bin)
        if not uv:
            print('Installing uv.', flush=True)
            run_installer('https://astral.sh/uv/install.sh', 'sh', temporary,
                          {'UV_INSTALL_DIR': str(local_bin), 'UV_NO_MODIFY_PATH': '1'})
            uv = local_bin / 'uv'
        documents = data / 'documents'
        documents.mkdir(exist_ok=True)
        project = documents / 'pyproject.toml'
        if not project.exists():
            write_file(project, (kit / 'document-tools.toml').read_text(encoding='utf-8'))
        browser, paths = browser_config(data, temporary, local_bin, extensions.get('playwright'))
        apply_user_settings(kit, config_dir, home, data, uv, documents, browser,
                            [str(local_bin), str(uv.parent), *paths])
        if not executable('rtk', local_bin):
            print('Installing RTK OSS for filtering long logs.', flush=True)
            try:
                run_installer('https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh',
                              'sh', temporary, {'RTK_EDITION': 'oss', 'RTK_INSTALL_DIR': str(local_bin),
                                                'RTK_SKIP_CHECKSUM': '0'})
            except (OSError, subprocess.CalledProcessError):
                print('RTK OSS is unavailable right now. Goose is configured and ready.')
        if shutil.which('goose') is None:
            profile = home / '.bashrc'
            current = profile.read_text(encoding='utf-8') if profile.exists() else ''
            path_line = 'export PATH="$HOME/.local/bin:$PATH"'
            if path_line not in current.splitlines():
                with profile.open('a', encoding='utf-8') as output:
                    output.write('\n' + path_line + '\n')
            print('Open a new Bash terminal so the goose command appears in PATH.')
        run([goose, '--version'])
        if desktop:
            install_desktop(temporary)
    print(f'Done. Goose settings: {config_dir}. Run goose from any working directory.')
    if not config.get('GOOSE_PROVIDER') and not os.environ.get('GOOSE_PROVIDER'):
        print('For the first run pick a provider and model in goose configure or Desktop settings.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--desktop', action='store_true', help='also install Goose Desktop via apt')
    options = parser.parse_args()
    try:
        main(options.desktop)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as error:
        print(f'Installation stopped: {error}', file=sys.stderr)
        sys.exit(1)
