---
name: generate-agents-md
description: Use when creating or revising repository-level AGENTS.md, CLAUDE.md, GEMINI.md, or similar agent instruction files; especially for durable project rules, onboarding guidance, coding standards, documentation requirements, testing workflow, or agent development process across any technology stack.
---

# Generate AGENTS.md

## Overview

Generate a durable, project-level `AGENTS.md` from repository facts. The output must describe how agents should work in this project across future tasks, not how to complete one current feature.

## Required Workflow

1. Establish the user-facing language before any other clarification:
   - If the user already explicitly requested Chinese, English, or another language, use that language without asking again.
   - Otherwise ask this bilingual question first: `后续我用中文还是英文和你确认信息并生成文档？ / Should I use Chinese or English for follow-up prompts and the generated file?`
   - Use the selected language for follow-up prompts, final explanations, and the generated instruction file unless the repository has an explicit conflicting language convention.
2. Inspect before writing:
   - Existing agent instruction files: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`.
   - Manifests and tooling: package/build/test configs, lockfiles, CI, Makefiles, workspace files.
   - Source layout, tests, docs, requirements/spec folders, examples, scripts, deployment config.
   - Existing public APIs, app entrypoints, module boundaries, import/export style, comments, and verification commands.
3. Identify project facts:
   - Tech stack or stacks, runtime, package manager, framework, test runner, formatter/linter, build/deploy path.
   - What can be edited directly and what is read-only reference.
   - Requirements/spec workflow and where design/interface docs belong.
   - Source ownership boundaries and recurring risk areas.
4. Classify the repository before choosing strictness:
   - `full`: mature product, SDK, platform, or service repo with durable docs and public contracts.
   - `sdk`: library/package repos where exports, adapters, examples, and package surface are the main risk.
   - `app`: frontend, mobile, desktop, or full-stack app where user flows, UI states, platform checks, and assets matter.
   - `backend`: API/service repos where endpoints, schemas, migrations, jobs, and observability matter.
   - `cli`: command-line tools where flags, stdout/stderr, exit codes, config files, and portability matter.
   - `data`: scripts, notebooks, ETL, analytics, or ML repos where reproducibility and input/output contracts matter.
   - `infra`: IaC, deployment, CI/CD, or operations repos where state, secrets, plan/apply, rollback, and environment safety matter.
   - `light`: small scripts, examples, docs-only, or config repos where heavyweight design/interface docs would be invented.
5. Ask only for other non-discoverable intent:
   - Whether the user wants strict docs-before-code, TDD, container-only verification, or lighter rules when not obvious from repo/context.
6. Generate or revise the target instruction file using the blueprint in `references/agents-md-blueprint.md`.
   - Preserve existing durable project rules unless they conflict with discovered project facts or the user's request.
   - Do not replace project-specific rules with generic boilerplate.
   - Do not invent design docs, interface docs, commands, package managers, CI, or public APIs that the repo does not support.
7. Keep the result project-wide:
   - Do not hard-code one ticket, version, milestone, temporary transition, or temporary plan as the project norm.
   - Mention a specific requirements path only as a general convention or when the repo itself defines it as a durable workflow.
8. Include concrete good and bad examples for fragile conventions:
   - Choose examples that match the repo and selected profile: design docs, interface/API docs, import/export style, comments/docstrings, command verification, CLI flags, infra safety, or data reproducibility.
9. Validate:
   - Run the bundled script from the skill folder, not from the target repository unless the script has been copied there.
   - Use `python3 <skill-folder>/scripts/validate_agents_md.py <path/to/AGENTS.md> --profile <profile>`.
   - Add `--forbid` terms for task-specific phrases that must not appear.
   - Add `--forbid-regex` or `--forbid-transient` when the task has version, ticket, branch, migration, sprint, or milestone wording that must not become project policy.
   - Run repo-appropriate whitespace checks such as `git diff --check`.

## Output Requirements

The generated `AGENTS.md` should normally cover:

- Project purpose and audience.
- Work boundaries and read-only references.
- Per-task development order.
- Requirements/spec entrypoints.
- Design document rules when the repo has design artifacts or non-trivial behavior changes.
- Interface/API document rules when the repo exposes APIs, commands, UI contracts, schemas, package exports, events, or config.
- Directory/module responsibilities.
- Coding conventions for the detected stack.
- Import/export or public surface rules that match the detected language and packaging model.
- External dependency, SDK, service, platform, or infrastructure boundaries.
- Documentation and comment rules, including structured examples.
- Testing, build, lint, format, verification, and environment rules.
- Git hygiene, delivery expectations, and final reporting rules.

Do not create a shallow checklist. The file should be actionable enough that another agent can start work without asking where code belongs, which docs must change, or what proof path is expected.

For small repositories, "actionable" can be brief. A `light` profile AGENTS.md should still state boundaries, workflow, commands, and examples, but it should not fabricate formal design or interface documents.

## Reference

Use `references/agents-md-blueprint.md` when composing the target file. It contains the reusable section blueprint and stack-specific adaptation prompts.

## Validation Script

Use the bundled `scripts/validate_agents_md.py` after writing. Resolve the path relative to this skill folder. Examples:

```bash
python3 /path/to/generate-agents-md/scripts/validate_agents_md.py ./AGENTS.md --profile full
python3 /path/to/generate-agents-md/scripts/validate_agents_md.py ./AGENTS.md --profile cli --allow-missing "design document rules"
python3 /path/to/generate-agents-md/scripts/validate_agents_md.py ./AGENTS.md --profile sdk --forbid "release-name" --forbid-transient
python3 /path/to/generate-agents-md/scripts/validate_agents_md.py ./AGENTS.md --profile full --require "import type" --require "design.md"
```

## Packaging

This repository is intended to be the skill folder itself. After publishing to GitHub, install with:

```bash
install-skill-from-github.py --repo <owner>/generate-agents-md --path . --name generate-agents-md
```

Restart Codex after installing.

## Common Mistakes

- Writing a ticket implementation plan instead of durable repo rules.
- Copying another project's AGENTS.md without replacing project facts.
- Inventing technology, commands, directories, or CI behavior not present in the repo.
- Applying the `full` or `sdk` profile to a tiny script, notebook, IaC, or docs-only repo without evidence.
- Flattening a monorepo into one rule set when packages, apps, services, or languages need separate sections.
- Using TypeScript/JSDoc examples in a Python, Go, Rust, Java, Swift, Kotlin, CLI, data, or infra repo without translating the convention.
- Listing methods or fields without explaining source, flow, side effects, and failure semantics.
- Omitting examples, which leaves future agents guessing what "good documentation" means.
- Running host-side commands when the repo requires container, simulator, remote, or CI verification.
