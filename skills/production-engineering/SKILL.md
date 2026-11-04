---
name: production-engineering
description: Plan, implement, or review production code changes. Use for API and schema changes, migrations, concurrency, access control, external integrations, refactors, and release readiness.
---

# Production engineering

1. Establish the contract. Read repository instructions, inspect the current diff, and trace the normal entry point through the affected boundaries. Identify callers, data shapes, invariants, and error behavior. For a bug, reproduce it or identify the missing evidence. State the acceptance condition and the first check that can falsify your approach.
2. Pick the smallest complete design. Follow the codebase's architecture and conventions. Keep responsibilities cohesive. Use composition, classes, and interfaces where they express existing invariants, ownership, or a genuine substitution boundary. Keep the public surface small. Reuse local primitives and document non-obvious decisions. Keep incidental edits out of the diff.
3. Review the affected failure paths. Check older inputs and version skew for contract changes. For persistence and remote side effects, reason about partial completion, retries, concurrent operations, and duplicate requests. For migrations, verify the order of deploy, data transition, and recovery. For security boundaries, trace inputs, identity, authorization, and secret handling from entry point to side effect. Apply the checks relevant to the change.
4. Verify through the real entry point. Run the focused regression check first and the applicable repository checks after it. Use an existing suite when it covers the scenario. Add a regression test when the defect or new contract would otherwise go untested. Inspect the complete failure output when a filter conceals the cause. Preserve unrelated working-tree changes.
5. Reread the final diff. For review, report actionable defects first, with severity, file and line, triggering scenario, and impact. Separate confirmed defects from unresolved questions. For implementation, state what changed, which commands ran, and their outcomes. Identify any remaining release check that requires an environment or credential you did not have.
