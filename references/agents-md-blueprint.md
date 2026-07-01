# AGENTS.md Blueprint

Use this blueprint to generate durable repository-level agent instructions. Adapt names, paths, commands, language, and strictness from the actual repository; do not copy placeholder wording as facts.

## Discovery Checklist

Before writing, inspect:

- Existing instructions: `AGENTS.md`, `CLAUDE.md`, `GEMINI.md`, `.cursor/rules`, project docs.
- Requirements/spec locations: `requirements/`, `docs/`, `specs/`, `design/`, tickets or PR docs.
- Manifests and tooling: `package.json`, `pyproject.toml`, `Cargo.toml`, `go.mod`, Gradle, Xcode, Makefile, Docker, CI.
- Source shape: entrypoints, public exports, services, components, adapters, tests, scripts, generated files.
- Verification path: install, lint, format, typecheck, test, build, e2e, emulator/simulator/container requirements.
- Changelog convention for the generated `AGENTS.md`: whether root `CHANGELOG.md` exists, what entry style it uses, which user-facing changes must be recorded there, and what to say if the repo has no changelog workflow yet.

## Empty Repository Gate

Before choosing a profile or drafting instructions, decide whether the target repository has enough facts to support project-level rules. Treat the repo as empty when it contains only `.git`, placeholder files, or no meaningful manifests, source, tests, docs, instructions, CI, scripts, requirements, or changelog.

For an empty repository, ask the user for enough detail before generating anything:

- Intended project type/profile: product, SDK/library, app, backend service, CLI, data/ML, infrastructure, docs-only, or other.
- Technology stack: language, runtime, package manager, framework, platform, database, deployment target, and required tooling.
- Expected shape: entrypoints, source/test/docs directories, generated files, examples, assets, and read-only references.
- Process rules: requirements/spec workflow, design notes, interface/API docs, changelog policy, release/versioning, branching, and delivery expectations.
- Verification rules: install, format, lint, typecheck, test, build, emulator/simulator/container, CI, deployment, rollback, or manual review commands.
- Standards: coding style, import/export or public surface rules, comments/docstrings, dependency boundaries, security/secrets policy, and examples to follow or avoid.

Do not fill these gaps from the template. Do not invent commands, package managers, CI, formal design/interface docs, public APIs, or changelog behavior. If the user explicitly asks for a placeholder anyway, use a provisional `light` profile and state that future agents must confirm project facts before introducing tooling or process.

## Profile Selection

Choose one validation and writing profile before drafting. The profile controls strictness; it must come from repo facts, not from the template.

| Profile | Use for | Avoid inventing |
| --- | --- | --- |
| `full` | Mature products, platforms, SDKs, or services with durable docs and public contracts | New documentation processes that the team does not use |
| `sdk` | Libraries, packages, SDKs, plugins, reusable modules | App UI workflows or service ownership that belongs to consumers |
| `app` | Frontend, mobile, desktop, or full-stack apps | Package-surface rules when there is no package API |
| `backend` | APIs, workers, jobs, services, data stores | UI-specific states unless the repo owns them |
| `cli` | Command-line tools and developer utilities | Formal API docs when flags/help text are the actual interface |
| `data` | Scripts, notebooks, ETL, analytics, ML experiments | Release/API rules when reproducibility is the main contract |
| `infra` | Terraform, Kubernetes, CI/CD, deployment, ops runbooks | Application coding rules outside the infra repo boundary |
| `light` | Small scripts, examples, docs-only repos, config repos | Design/interface docs, module docs, or heavy process gates |

When a monorepo contains multiple profiles, write a short root section plus package/app/service-specific subsections. Do not flatten conflicting frontend, backend, mobile, SDK, data, and infra rules into one generic rule.

## Recommended Sections

### Project Purpose

Describe what the project is, who it serves, and the business/runtime surface it owns. Keep it long-lived. Do not mention one-off tickets as the project purpose.

### Work Boundaries

State what can be edited directly, what is read-only reference, and which concerns belong to sibling repos, services, SDKs, infra, generated artifacts, or external vendors.

### Per-Task Development Order

Include a numbered workflow:

1. Check worktree state.
2. Read the requested requirements/spec.
3. Read current implementation and related docs.
4. Confirm project/module boundary.
5. Update design and interface docs when behavior or contracts change.
6. Add tests or fixtures before implementation when logic changes.
7. Implement in the correct module.
8. Sync comments, examples, docs, public surfaces, and root `CHANGELOG.md` when the change is user-facing or contract-affecting and the repo has a changelog workflow.
9. Run repo-standard verification.
10. Report changed files, proof commands, and known gaps.

### Requirements Entry

Explain where requirements live, what to do if no requirement is specified, and how to avoid turning one requirement into global policy.

### Design Document Rules

Require design docs for non-trivial behavior changes when the repo has, expects, or benefits from durable design artifacts. In `light`, `cli`, `data`, or `infra` repos, this may be a short design note, issue spec, runbook section, ADR, notebook preface, or plan comment instead of a formal `design.md`.

Cover the applicable items:

- Goal, visible behavior, acceptance criteria, and non-goals.
- Current state and affected modules.
- Data flow, state flow, side effects, and platform differences.
- Error/cancel/empty states and fallback behavior.
- Compatibility and mapping boundaries.
- Major decisions and rejected alternatives.
- Testing and verification strategy.

Good example:

```md
## Retry Policy Design

### Goal

When a request fails with a retryable network error, retry up to two times before showing the existing failure UI.

### Boundaries

- The API client owns retry timing.
- UI components only render loading, success, and failure states.
- The analytics module records final success or failure, not every retry attempt.

### Data Flow

1. Component calls `loadItems()`.
2. API client retries retryable failures.
3. Component receives one final result.
4. Analytics receives one final event.
```

Bad example:

```md
Update retry logic and handle errors.
```

Do not require this section to create a new formal document if the repo has no durable place for such docs. Instead, state the repo's actual lightweight decision record.

### Interface/API Document Rules

Require interface or contract docs when changing public APIs, URL parameters, CLI flags, props/events, SDK methods, service endpoints, schemas, config, telemetry, data outputs, deployment variables, or operator commands. In some repos the interface doc is README help text, generated API docs, OpenAPI, Storybook, CLI `--help`, schema files, migration notes, notebooks, or runbooks.

Cover the applicable items:

- Import path, command, endpoint, screen, or entrypoint.
- Parameter table with type, required/default behavior, source, and destination.
- Return/result shape and success/cancel/failure semantics.
- Side effects, persistence, network calls, emitted events, telemetry.
- Examples for minimal use, core flow, and failure flow.
- Compatibility notes for legacy fields or old callers.

Good example:

```md
## `loadItems(params)`

- Import path: `src/features/items/loadItems`
- Call timing: after the user selects a workspace.
- Parameters:

| Field | Type | Required | Source | Behavior |
| --- | --- | --- | --- | --- |
| `workspaceId` | `string` | yes | route params | Selects the item scope. |
| `cursor` | `string` | no | previous result | Loads the next page when present. |

- Returns: `{ items, nextCursor }`; `nextCursor: null` means no more pages.
- Failure: rejects with a typed application error; UI maps it to the existing failure state.
```

Bad example:

```md
`loadItems()` loads data.
```

Profile-specific interface examples:

- SDK/library: export path, factory/options, public type, returned result, error model, package surface.
- App/frontend/mobile: route, screen, component props/events, state transitions, assets, accessibility, platform permissions.
- Backend/API: endpoint, method, auth, schema, status codes, side effects, migrations, observability.
- CLI: command, flags, stdin/stdout/stderr, exit code, config files, shell portability.
- Data: input dataset, output artifact, deterministic seed, schema, refresh cadence, reproducibility command.
- Infra: variable, secret, state backend, plan/apply command, rollback, environment blast radius.

### Directory and Module Responsibilities

Map the actual top-level directories and important modules. Explain where new code belongs and which files should remain thin orchestration layers.

For monorepos, split responsibilities by workspace/package/app/service. Include ownership boundaries such as "root config only," "shared packages," "generated clients," "examples," "fixtures," and "deployment manifests." State whether changes must be repeated across packages or whether one package is the source of truth.

### Development Standards

Derive stack-specific rules from the repo:

- Frontend: components, state, routing, styling, assets, accessibility, responsive behavior, browser verification, visual regression.
- Backend/API: handlers, services, repositories, schemas, database changes, jobs, observability, error contracts.
- SDK/library/plugin: public exports, adapter boundaries, package surface tests, examples, versioning, generated types.
- Mobile: platform entrypoints, simulator/emulator validation, app intents, permissions, lifecycle.
- CLI/tooling: commands, flags, stdin/stdout/stderr, exit codes, config files, shell portability.
- Data/script projects: deterministic inputs/outputs, idempotency, large files, notebooks, reproducibility.
- Infra/ops: plan before apply, environment targeting, state and lock handling, secrets, rollback, production safety.
- Docs/content: source format, generated output, link checks, screenshots/assets, publishing path.

### Import and Export Standards

For TypeScript-like stacks, prefer this only when it matches the repo:

- Imports centralized at top.
- Runtime imports grouped separately from `import type`.
- Public exports centralized at file bottom.
- `export type` separated from value exports.
- Directory entrypoints export only stable public surface.

For other languages, adapt to equivalent conventions:

- Python: top imports, no wildcard imports, `__all__` only for deliberate public API.
- Go: package names stable, internal packages for private code, exported identifiers documented.
- Rust: explicit `pub` surface, `mod` boundaries clear, no accidental re-export.
- Java/Kotlin: package boundaries match source layout, public classes/interfaces documented, avoid wildcard imports if style forbids them.
- Swift: access control is explicit, platform-specific imports are isolated, public APIs have doc comments.
- Ruby/PHP: namespace/module boundaries are explicit, autoloading conventions are followed, no hidden global side effects.
- C/C++: headers define the public surface, internal symbols stay private, include order follows repo tooling.
- Infra/data/docs: replace import/export rules with public surface rules such as module outputs, variables, generated artifacts, notebook outputs, CLI commands, or published docs.

If a repo has no meaningful import/export convention, state the actual public surface instead of forcing this section.

### External Dependency Boundaries

State which external SDKs, services, generated clients, platform APIs, or infrastructure modules should be consumed rather than reimplemented. Legacy or wire-format compatibility belongs in adapters/normalizers, not broad public surfaces.

### Documentation, Changelog, and Comments

The generated `AGENTS.md` must include a clear changelog rule for the target project, not merely this skill repository. When root `CHANGELOG.md` exists or the user asks for changelog coverage, tell agents to record concrete user-facing changes in root `CHANGELOG.md`, not in README or other overview docs. Changelog updates are expected for behavior changes, public API or CLI changes, migrations, compatibility changes, and user-visible documentation changes. Keep entries factual and outcome-focused; do not write release-bound prohibitions such as "version X must not do Y". If no root `CHANGELOG.md` exists, the generated `AGENTS.md` should say not to invent one without user or repository evidence.

Require structured comments for public APIs, complex helpers, adapters, mappings, error semantics, platform differences, and non-obvious decisions. Include good and bad examples tailored to the language.

Choose examples in the target repo's language or artifact type. Do not paste TypeScript/JSDoc into non-TypeScript repos unless the repo actually uses it.

Good TypeScript/JSDoc example:

```ts
/**
 * @description Converts API item records into UI card state without exposing wire fields.
 * @param records API records returned by the item service.
 * @returns UI card states; invalid records are excluded and reported by the caller.
 */
function mapItemCards(records: ApiItemRecord[]): ItemCardState[] {
  return records.map(mapOneItemCard);
}
```

Bad example:

```ts
// Handles data.
function map(data: any) {}
```

Good Python/docstring example:

```py
def map_item_cards(records: list[ApiItemRecord]) -> list[ItemCardState]:
    """Convert API item records into UI card state without exposing wire fields.

    Args:
        records: API records returned by the item service.

    Returns:
        UI card states. Invalid records are excluded and reported by the caller.
    """
```

Good Go/doc comment example:

```go
// MapItemCards converts API item records into UI card state without exposing wire fields.
// Invalid records are excluded and reported by the caller.
func MapItemCards(records []ApiItemRecord) []ItemCardState {
    // ...
}
```

For CLI, data, infra, or docs repos, examples can show help text, config comments, notebook prefaces, Terraform variable descriptions, or runbook snippets instead of code comments.

### Testing and Verification

List exact repo-standard commands for install, format, lint, typecheck, test, build, e2e, emulator/simulator/container workflows. If commands are unavailable in the current shell but documented in the repo, preserve the documented workflow and explain environment assumptions.

Profile-specific proof paths:

- SDK/library: package surface tests, type-contract tests, example builds, CJS/ESM or platform package checks.
- App/frontend/mobile: unit tests, rendered smoke tests, screenshots, accessibility checks, simulator/emulator/browser checks.
- Backend/API: service tests, contract tests, database migration checks, integration tests, local stack or container checks.
- CLI: help output, sample commands, exit-code checks, stdin/stdout/stderr behavior, shell portability.
- Data: deterministic rerun, fixture comparison, schema validation, output artifact checks, large-file policy.
- Infra: validate/plan, policy checks, secret scans, environment targeting, rollback/runbook verification.
- Light/docs: whitespace check, link check, formatter, targeted manual review.

### Git and Delivery

Require checking status before edits, preserving user changes, avoiding unrelated rewrites, and reporting verification evidence. Include branch, commit, and PR rules only if the repo has durable conventions.

## Quality Bar

The final `AGENTS.md` should be specific enough to guide implementation without being a copy of one feature plan. It should include concrete examples wherever a future agent might otherwise guess.
