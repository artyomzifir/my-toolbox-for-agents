# Goose R&D Kit

A one-user Ubuntu setup for [Goose](https://github.com/aaif-goose/goose) that turns a fresh CLI or Desktop install into a working research and engineering agent.

It installs Goose, Playwright MCP, LLM routing rules, document tooling (Docling, pandas, matplotlib), and a pinned library of 209 upstream skills plus one kit-owned skill — then links a curated 11-skill engineering set and 13 research/ML skills into Goose, so they are available in every session.

## What it is

| Component | Purpose |
|---|---|
| `install.sh` / `install.py` | Idempotent installer; run as a regular user, not root |
| `portable-research-library/` | Pinned snapshot of upstream skills, commands and plugins with a local index |
| `_vendor/` | Vendored PyYAML (MIT) so `install.py` can parse `config.yaml` without pip or touching system Python |
| `templates/` | Rules the installer injects into Goose (`templates/.goosehints` research policy, `templates/production-rules.md` skill routing) plus `PROJECT_STATE.md` and `SOURCES.md` project templates |
| `start-research.sh` | Session wrapper: project state file, turn limits, repetition guard |
| `document-tools.toml` | `uv` project for document and chart work |

## Requirements

- Ubuntu 22.04+ (x86_64 or ARM64), Python 3.10+
- Regular user account; `sudo` is only requested for the optional Desktop package
- Network access to GitHub releases, PyPI and the npm registry
- Windows users: run the CLI inside WSL2; native Desktop plus WSL tooling is a separate manual setup

## Installation

```bash
git clone git@github.com:artyomzifir/my-toolbox-for-agents.git
cd my-toolbox-for-agents
./install.sh                 # CLI only
./install.sh --desktop       # also install Goose Desktop via apt
```

Then open a new Bash terminal and run `goose`. On first start, pick a provider and model in `goose configure` or in Desktop settings.

The installer:

- installs Goose CLI into `~/.local/bin` and `uv` if they are missing;
- enables the bundled `developer`, `skills`, `todo` and `chatrecall` extensions and configures Playwright MCP (Firefox, absolute paths, pinned version);
- merges settings into `config.yaml` with a backup instead of overwriting; your provider, keys and third-party extensions are preserved;
- copies the payload to `~/.local/share/goose-research-kit/bundle-<hash>/` and symlinks the selected skills into Goose's skill directory;
- installs Docling and friends on first use through `uv`;
- installs RTK OSS when its release is reachable; failure there does not break the install.

Re-running is safe: managed rules and skills are replaced, `config.yaml` is backed up, and skills you wrote yourself are left alone.

Set `GOOSE_PATH_ROOT=/absolute/path` to keep `config.yaml` under that root instead of `~/.config/goose`.

## What gets enabled

| Kind | Items |
|---|---|
| Extensions | `developer`, `skills`, `todo`, `chatrecall`, `playwright`, plus Goose's built-in `web-search` |
| Engineering skills | `planning-and-task-breakdown`, `api-and-interface-design`, `deprecation-and-migration`, `code-review-and-quality`, `security-and-hardening`, `kiss`, `solid`, `systematic-debugging`, `test-driven-development`, `verification-before-completion` |
| Research skills | `literature-review`, `scientific-critical-thinking`, `hypothesis-generation`, `experimental-design`, `statistical-analysis`, `validate-data`, `ml-paper-writing`, and six ML/evaluation skills from the `ml-core` profile |
| Kit-owned skill | `conventional-commits` — Conventional Commits 1.0.0 procedure plus a `commit-msg` hook; part of the `software-core` profile, so it is linked like any other skill |
| Session defaults | `GOOSE_MAX_TURNS=30`, compact threshold 0.6, one concurrent subagent, cost display on |

Invoke a skill directly from the CLI, for example `/skills code-review-and-quality`.

## Skill profiles

Profiles are the selection mechanism; only skills from profiles are linked, everything else stays in the library unindexed.

| Profile | Skills | Content |
|---|---|---|
| `research-core` | 7 | Review, critique, hypotheses, experiment design, statistics, data validation, paper writing |
| `research-expanded` | 16 | Additional scientific procedures; try `research-core` first |
| `ml-core` | 6 | ML engineering and evaluation |
| `software-core` | 11 | Planning, contracts, migrations, review, security, KISS, SOLID, debugging, TDD, verification, commit conventions |
| `token-style` | 1 | Caveman, short answers on explicit request |
| `focused-checks` | 2 | Diagnosis and sufficient-verification procedures |

## The library

`portable-research-library/` is a snapshot: 209 upstream skills plus the kit-owned `conventional-commits`, 22 command and agent files, 19 plugin manifests, and five public Codex prompt files. Nothing is loaded into context by default; the agent searches the index and reads one to three relevant files.

```bash
python3 portable-research-library/catalog.py profiles
python3 portable-research-library/catalog.py search "literature review" --limit 5
python3 portable-research-library/catalog.py show <id> --text
python3 portable-research-library/catalog.py verify
python3 portable-research-library/catalog.py activate --profile research-core --project . --apply
```

Search is lexical over metadata, mostly English, with no network or model calls. `verify` checks every file against `files.sha256.json`. `activate` links a profile into a project's `.agents/skills` instead of the global Goose directory.

Full listing: [CATALOG.md](portable-research-library/CATALOG.md). Library notes: [README.md](portable-research-library/README.md).

## Sources

Every snapshot is pinned to a commit. Versions, URLs and licenses also live in `sources.lock.json` and `catalog.json`.

| Source | Upstream | Pinned commit | License |
|---|---|---|---|
| Addy Osmani Agent Skills | https://github.com/addyosmani/agent-skills | `301b02b12bff` | MIT |
| JordanCoin Coding Skills | https://github.com/JordanCoin/codingskills | `d990b56b72f3` | see upstream |
| Superpowers | https://github.com/obra/superpowers | `22f0b463e7a5` | MIT |
| Anthropic Skills | https://github.com/anthropics/skills | `ca45fc496a34` | see upstream |
| Anthropic Knowledge Work Plugins | https://github.com/anthropics/knowledge-work-plugins | `2574e29377c7` | see upstream |
| Anthropic Claude Plugins Official | https://github.com/anthropics/claude-plugins-official | `a7ba5b93db0c` | Apache-2.0 |
| OpenAI Plugins | https://github.com/openai/plugins | `0722921d5542` | MIT/Apache-2.0 per plugin |
| OpenAI Codex prompts | https://github.com/openai/codex | `6c4fa86838df` | see upstream |
| Orchestra Research AI Research Skills | https://github.com/Orchestra-Research/AI-research-SKILLs | `773a52944ba4` | see upstream |
| K-Dense Scientific Agent Skills | https://github.com/K-Dense-AI/scientific-agent-skills | `a25cf9ec00e2` | see upstream |
| Caveman | https://github.com/JuliusBrussee/caveman | `2e068f735253` | see upstream |
| This kit (own skills) | https://github.com/artyomzifir/my-toolbox-for-agents | current `main` | MIT |

Upstream files are kept in their original structure with their licenses and notices. A permissive license on a procedure does not license the third-party services, models or data it mentions. Selection was conservative: material without a confirmed permissive license, or with explicit restrictions, was not added.

## Kit-owned skill: conventional-commits

It lives in the library like every other skill, under `portable-research-library/upstream/goose-research-kit/skills/conventional-commits/`, and is registered in the catalog with a `goose-research-kit` source and no upstream commit. The directory holds the procedure, its validator and its tests:

- `SKILL.md` — type and scope selection, breaking-change markers, footers, examples, review checklist;
- `scripts/commit-msg` — POSIX `sh` hook checking type set, header format, 72-character limit, blank line before the body, `BREAKING CHANGE` casing, footer tokens and autosquash markers;
- `tests/run-tests.sh` — 20 cases covering accepted and rejected messages.

Install the hook in any repository:

```bash
cp portable-research-library/upstream/goose-research-kit/skills/conventional-commits/scripts/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

## Working in a research project

The installer turns `templates/.goosehints` and `templates/production-rules.md` into the global Goose rules. For a research project, copy `templates/PROJECT_STATE.md` and `templates/SOURCES.md` into it, then start the session through the wrapper:

```bash
bash start-research.sh          # new session
bash start-research.sh --resume # continue
```

The wrapper injects `PROJECT_STATE.md` on every turn via `GOOSE_MOIM_MESSAGE_FILE` and caps repeated identical tool calls. Keeping state is still the agent's job by instruction, not a knowledge base: concurrent CLI and Desktop sessions must not rewrite the same `PROJECT_STATE.md` independently.

## Updating

```bash
git pull
./install.sh
```

The installer re-registers its own rules and skills, replaces its stale symlinks, and retires skills it no longer manages. Updating the pinned upstream snapshot is a separate manual step: refresh `portable-research-library/upstream/`, then regenerate `catalog.json`, `CATALOG.md`, `sources.lock.json` and `files.sha256.json` before running `catalog.py verify`.
