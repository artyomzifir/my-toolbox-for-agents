## Engineering skills

Start with the repository instructions. Load procedures for the task; for a small edit use only the applicable skills and the project's checks.

- For multi-step implementation use `planning-and-task-breakdown`. Keep the plan where the project expects it, or in the chat when the project needs no separate file.
- For a public contract use `api-and-interface-design`; for retiring an old API or migrating data use `deprecation-and-migration`; for authorization and trust boundaries use `security-and-hardening`.
- For readability and simplification use `kiss`; for responsibility boundaries, interfaces and classes use `solid`. Apply them within the project's paradigm.
- For a defect start with `systematic-debugging`; for a behavior change use `test-driven-development`; before claiming completion use `verification-before-completion`. When Superpowers references `superpowers:<name>`, load the skill in Goose by name without the prefix.
- For reviewing a substantial diff use `code-review-and-quality`. Open Addy's shared checklists through Developer using paths relative to the skill directory.
- For commit messages follow `conventional-commits`: type, scope, imperative description, and a `BREAKING CHANGE` marker when behavior breaks. Install its hook with `cp <skill>/scripts/commit-msg .git/hooks/commit-msg`.

Keep existing edits and run checks with the project's own commands. Confirm worktree changes and external service calls against the repository instructions and the authority the task grants.
