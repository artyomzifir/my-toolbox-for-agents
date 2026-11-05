# Portable procedure library for a research agent

A snapshot of open-source skills, commands and plugins, refreshed on 4 November 2026. The library ships with Goose R&D Kit. Versions and licenses are recorded in the catalog and `sources.lock.json`.

The snapshot holds 209 upstream skills, 22 command and agent procedure files, 19 plugin configurations and manifests, five public Codex prompt files, and one skill owned by this kit.

## Purpose

The library tests the hypothesis that an agent lacks working procedures, skills and instructions. It contains material for scientific search, literature review, evidence critique, hypotheses, experiments, statistics, ML engineering, paper writing, coding and result verification.

Readiness varies. A file being present, or passing a format check, does not prove quality on your tasks. Model runs, OAuth/MCP setup and auxiliary API calls were not performed here.

## Sources

- Anthropic Skills: open skill examples; document skills (docx/pdf/pptx/xlsx) with separate restrictions are not included.
- Anthropic Knowledge Work Plugins: selected working plugins for data, engineering, search and task organization. This is Cowork, a separate Anthropic product; it is not ChatGPT Work.
- Anthropic Claude Plugins Official: selected plugins with development, review, MCP and project-organization procedures.
- OpenAI Plugins: selected material with confirmed MIT/Apache-2.0 licenses. Some curated plugins were written by third parties, not OpenAI. Public availability of the remaining plugins does not imply permission to redistribute.
- Orchestra Research AI Research Skills: a library of ML engineering, evaluation and research procedures.
- K-Dense Scientific Agent Skills: selected general-science procedures, statistics and result presentation.
- Caveman: skills for short answers, diagnosis and check completion. Activated by the `token-style` and `focused-checks` profiles.
- Addy Osmani Agent Skills: five procedures for planning, contracts, migrations, review and security, with shared checklists.
- JordanCoin Coding Skills: nine skills about engineering principles. `kiss` and `solid` belong to the `software-core` profile.
- Superpowers: a direct snapshot of the obra project. `software-core` uses its linked diagnosis, TDD and verification procedures; the wider process stays in the catalog.
- OpenAI Codex: five public files with base instructions, history compaction and a review rubric. These are Codex CLI sources, not a complete ChatGPT Work or Claude Code system prompt.
- Goose R&D Kit: the kit-owned `conventional-commits` skill, maintained in this repository rather than imported.

Exact URLs, commit SHAs and upstream license texts live in `sources.lock.json` and `catalog.json`. License selection was conservative: material without a confirmed MIT/Apache-2.0 license, or with explicit restrictions, was not added. Keep the included notices and licenses. A permissive license on a procedure does not license the third-party services, models or data it mentions.

## Wiring into Goose

Goose R&D Kit already carries the routing rules in `templates/.goosehints`. To move the library into another project, copy the `portable-research-library/` directory and add the research rules from the kit's `templates/.goosehints` to that project's rules.

By default the library does not inject hundreds of skills into context and does not connect external services. The agent searches procedures with a local command, reads one to three relevant files, and uses them as working guidance.

```bash
python3 portable-research-library/catalog.py profiles
python3 portable-research-library/catalog.py search "literature review" --limit 5
python3 portable-research-library/catalog.py search "hypothesis experiment" --limit 5
python3 portable-research-library/catalog.py search "evaluation transformers" --limit 5
python3 portable-research-library/catalog.py verify
```

Search is lexical over metadata, mostly English, with no model or network calls. To read a file, use the path from the result or `catalog.py show ID --text`.

## Linking a small profile natively

A selected set can be linked into a project's `.agents/skills`. Preview first:

```bash
python3 portable-research-library/catalog.py activate \
  --profile research-core --project .
```

Then apply:

```bash
python3 portable-research-library/catalog.py activate \
  --profile research-core --project . --apply
```

On Linux this creates symlinks to the source directories, so keep the library in place afterwards. On Windows add `--copy`; the copy gains source metadata and a license copy. For `software-core`, use link mode or `install.sh` under WSL so paths to Addy's shared checklists stay valid. Existing skills are never overwritten; a name conflict stops the run before any change. Re-running link mode skips links that already exist.

This is an import of source skills, not an automatic port of every tool they mention. Compatibility flags are visible in `catalog.json`. Claude-specific frontmatter fields, paths, sibling resources and external services need checking in Goose. A procedure that needs its own API or package does not get it from the import. After importing, start a new session and run `goose skills list`.

## Integrations

`integrations.json` lists MCP configurations and helper manifests of the selected plugins with paths to their sources. It is material for adapter work. Such entries do not mean a service is connected, the user is authorized, or a given server works with Goose.

For ordinary MCP servers, move a supported stdio/HTTP transport into Goose settings and configure authorization per the service's own documentation. Internal Work/Cowork connectors and their identifiers cannot be turned into a connection by copying JSON.

## Public prompts

`upstream/openai-codex` keeps public examples of base instructions, compaction and review with their original license. Some file names reference specific models; that is not a recommendation to pick those models today. The prompts assume Codex tool schemas, permission systems and runtime. Treat them as analysis material and sources for targeted adaptations.

The kit's research rules are a policy written for this setup. They do not reproduce closed system instructions from Work or Claude Code. They define the order of work on evidence, state, experiments, progress and stopping; hard limits still need runtime support and API-side control.

## Testing the "missing procedures" hypothesis

On one API model, with identical tools and budget, compare:

1. Starter without the library.
2. Starter with the shared research policy from the kit's `templates/.goosehints`.
3. The same policy plus one to three selected procedures.

Use real tasks and record constraint retention after compaction, reference accuracy, completeness, user interventions, cost, time and repeated actions. Test additional connectors as a separate change so it is clear where any improvement came from.

The library does not reproduce either product in full. A strong procedure can improve results; base model quality and runtime correctness still matter.
