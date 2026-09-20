# Project Overview

- README.md is used to desribe the project. Use to get the current state and take care off keeping it up-to-date

# Source Code & Project Management

## Git Workflow

- All source code is managed with **Git**.
- Changes and implementations **must always be done on a separate branch** — never commit directly to `main` unless the user explicitly requests it.
- Branch naming convention:
  - Features: `feature/short-description`
  - Bug fixes: `fix/short-description`
- Commits should be made **early and often** — prefer small, focused commits over large batches.
- All commits must follow the **[Conventional Commits](https://www.conventionalcommits.org/)** specification:
  - Format: `<type>(<optional scope>): <description>`
  - Common types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`, `style`, `ci`
  - Example: `feat(meter): add kWh reading entry form`

## GitHub Interaction

- The repository is hosted on **GitHub**.
- Any interaction with GitHub (pull requests, issues, releases, etc.) must be done using the **`gh` CLI tool** (GitHub CLI).
- Do not use the GitHub web UI or REST API directly.

# Repository Structure

## docs/feature/

Contains feature and requirements definitions as simple Markdown files. Each file describes a single feature or requirement.

- **Naming convention:** `docs/feature/NNNN_short_description.md` (zero-padded 4-digit number, e.g. `0001_add_meter.md`)
- Files are written in plain Markdown and focus on *what* is needed, not *how* it is implemented.
- New features should always get a corresponding file here before implementation begins.

## docs/adr/

Contains Architecture Decision Records (ADRs) — documents that capture significant design decisions that directly affect the architecture and source code.

- **Naming convention:** `docs/adr/NNNN_short_description.md` (zero-padded 4-digit number, e.g. `0001_choose_backend_framework.md`)
- Each ADR documents: the context, the decision made, and the consequences/rationale.
- ADRs are append-only: once recorded, existing ADRs should not be rewritten. Superseded decisions get a new ADR referencing the old one.


