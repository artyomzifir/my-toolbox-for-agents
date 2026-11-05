---
name: conventional-commits
description: Writes and checks commit messages that follow Conventional Commits 1.0.0. Use whenever creating, amending, squashing or reviewing a commit message, when asked to commit changes, or when a commit fails a commit-msg hook. Covers type and scope choice, breaking-change markers, footers, and SemVer mapping.
---

# Conventional Commits

Rules come from [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/) (specification items 1–16). This file is the working procedure. If the two disagree, the specification wins.

## When to Use

- Before any `git commit`, `--amend`, `rebase -i` (reword/squash), or `git merge --squash`.
- When reviewing history (`git log`, a pull request) for format compliance.
- When a `commit-msg` hook rejects a message.

## Anatomy

```
<type>[optional scope][!]: <description>
                                    ← blank line required when a body follows
[optional body]

[optional footer(s)]
```

Hard requirements from the specification:

1. The header starts with a noun type, followed by an optional scope in parentheses, an optional `!`, and a required colon plus space.
2. The description follows immediately after `: ` and summarizes the change.
3. A body begins exactly one blank line after the description.
4. Footers begin one blank line after the body; each is `Token: value` or `Token #123`.
5. A footer token uses `-` instead of whitespace (`Reviewed-by`). The exception is `BREAKING CHANGE`.
6. `BREAKING CHANGE` must be uppercase; `BREAKING-CHANGE` is a synonym.
7. Case is otherwise insignificant to parsers, but this project keeps type, scope and the start of the description lowercase.

## Choosing the Type

| Type | When to use | SemVer |
|---|---|---|
| `feat` | new functionality for users or an API | MINOR |
| `fix` | a bug fix | PATCH |
| `perf` | a change that makes code faster without changing behavior | — |
| `refactor` | restructuring code without changing behavior | — |
| `docs` | documentation only | — |
| `test` | tests only | — |
| `build` | build system, dependencies, artifacts | — |
| `ci` | CI configuration and scripts | — |
| `style` | formatting, whitespace, semicolons (not logic) | — |
| `chore` | routine work that fits nothing else | — |
| `revert` | reverting an earlier commit | — |

Selection rules:

- A change alters observable behavior for users → `feat`, not `refactor` or `chore`. New behavior someone could adopt is always `feat`.
- A commit removes incorrect behavior → `fix`, even when the edit lands in tests or docs.
- No type fits → try splitting the commit first. Add a new type only deliberately, and use it consistently across the repository.
- A commit fits two types → split it into two commits.

## Scope

- A noun naming the code area: `feat(parser):`, `fix(api):`, `docs(readme):`.
- One level, lowercase, no spaces. `feat(auth-token):` and `fix(cli/config):` are acceptable; do not nest deeper.
- Omit the scope when the change spans the project. Do not invent a scope "just in case".

## Description

- Imperative mood, like an email subject: `add`, `fix`, `remove` — not `added`, `fixes`, `adding`.
- Lowercase first letter unless the first word is a proper noun or acronym.
- No trailing period.
- Keep the whole header at or under 72 characters. If it does not fit, shorten the meaning and move detail into the body.
- Never write `update code`, `fix bug`, `changes`. The description must name the concrete change.

## Body

- Explain *why*, not *what*: what was wrong and why this approach. The diff already shows what changed.
- Free-form text, paragraphs separated by blank lines, wrapped at roughly 72–80 columns.
- Reference issues in footers (`Refs: #123`, `Closes: #123`), not in the header.

## Breaking Changes

Mark a breaking change in at least one of two ways:

- `!` before the colon: `feat(api)!: drop v1 endpoints`
- a footer: `BREAKING CHANGE: v1 endpoints removed; migrate to /v2.`
- Both together are valid when the footer clarifies migration.

Details:

- `BREAKING CHANGE` may appear in a commit of any type (`refactor!:`, `chore!:`).
- With only `!`, the separate footer is optional: the description is treated as the breaking-change description. Add the footer anyway when migration is not obvious.
- SemVer: any breaking change is MAJOR, regardless of type.
- `BREAKING CHANGE` in lowercase as a footer token is an error.

## Footers

```
Reviewed-by: Z
Refs: #123
Closes: #124
```

- Token uses `-`; value follows `: ` (or ` #` for numbers).
- Use the tokens the repository already recognizes. Do not invent new ones without need.
- Never add `Co-authored-by`, `Signed-off-by` or similar attribution trailers on your own. The commit belongs to the repository owner; add such a trailer only when the owner explicitly asks for it.

## Revert

```
revert: feat(api): send welcome email

This reverts commit 1234abc.
```

The body with `This reverts commit <sha>.` is git's convention; the header describes the reverted change.

## Workflow

1. Decide what changes and for whom. If the commit mixes two independent changes, split it.
2. Pick the type from the table. Unsure between `feat` and `refactor`? Check whether observable behavior changes.
3. Add a scope when the change is localized.
4. Write the description in imperative mood, at most 72 characters including the prefix.
5. Mark breaking changes with `!` and/or a `BREAKING CHANGE:` footer.
6. Add a body only when the "why" needs context. One blank line after the header.
7. Run the check: `git commit` with the hook installed, or manually:

```bash
sh scripts/commit-msg .git/COMMIT_EDITMSG
```

## Examples

Valid:

```
feat(parser): add support for arrays
fix: prevent racing of requests
docs: correct spelling of CHANGELOG
feat(lang): add Polish language
perf(render): cache resolved theme tokens
feat(api)!: send an email when a product is shipped
chore!: drop support for Node 6

BREAKING CHANGE: use JavaScript features not available in Node 6.
```

Invalid, and why:

| Message | Reason |
|---|---|
| `Added new parser` | no type |
| `feat add parser` | no `: ` |
| `feat:Add parser` | no space after the colon |
| `feat: add parser.` | trailing period in the description |
| `feat: Add parser` | uppercase first letter (project style) |
| `feat: added parser` | past tense instead of imperative |
| `update: change stuff` | type outside the accepted set |
| `feat(api): drop endpoints breaking change: ...` | `BREAKING CHANGE` not in a footer and not uppercase |
| `feat: add parser\nbody` | no blank line before the body |
| `fix: update code` | description does not name the change |
| `feat: parser + bugfix + docs` | several unrelated changes in one commit |

## Review Checklist

- [ ] Type is present and matches the change.
- [ ] Format is `<type>(<scope>)!: <description>` with a colon and space.
- [ ] Description is imperative, has no trailing period, and the header fits in 72 characters.
- [ ] One commit covers one logical change.
- [ ] Body is separated by a blank line and explains *why*.
- [ ] Breaking changes are marked with `!` and/or an uppercase `BREAKING CHANGE:` footer.
- [ ] Footers are correct: hyphenated tokens, values after `: `.
- [ ] The `commit-msg` hook passes.

## Guardrail (optional but recommended)

Keep the format automatic instead of relying on memory:

```bash
cp scripts/commit-msg .git/hooks/commit-msg && chmod +x .git/hooks/commit-msg
```

The hook rejects a commit with a message naming the broken rule. Bypass with `git commit --no-verify`, at your own risk.

For shared repositories, run the same check in CI over every new commit.
