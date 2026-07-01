# Changelog

All notable user-facing changes to this skill are documented here.

## Unreleased

- Added guidance that concrete change history belongs in the repository-root `CHANGELOG.md`, while README should stay focused on stable usage and maintenance documentation.
- Updated the skill workflow to inspect and preserve changelog conventions, and to include changelog update rules when generating repository-level agent instructions.
- Clarified that generated project `AGENTS.md` files must explicitly include the changelog rule when a repository uses root `CHANGELOG.md`.
- Made the target-project changelog requirement explicit: generated `AGENTS.md` files should include a clear changelog rule, not only this skill repository.
