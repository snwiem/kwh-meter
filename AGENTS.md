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

## GitHub Project & Issue Tracking

All work is tracked via **GitHub Issues** linked to the **kwh-meter** project board (https://github.com/users/snwiem/projects/7).

The project is linked to the `snwiem/kwh-meter` repository and is accessible directly from the repo's **Projects** tab.

### Issue Templates

Four issue templates are defined in `.github/ISSUE_TEMPLATE/`. Always use the appropriate template when creating a new issue:

| Template | Use for |
|---|---|
| `feature.md` | New capabilities or requirements |
| `bug.md` | Something broken or behaving incorrectly |
| `chore.md` | Infrastructure, config, dependency updates |
| `documentation.md` | Documentation-only changes |

### Labels

Every issue must have at least one label from each relevant axis:

| Axis | Labels |
|---|---|
| **Type** | `type:feature`, `type:bug`, `type:chore`, `type:documentation` |
| **Scope** | `scope:frontend`, `scope:backend`, `scope:database`, `scope:infra` |
| **Priority** | `priority:high`, `priority:low` |

Workflow state is tracked exclusively via the **project board Status field** — never via labels.

### Project Board Status Field

The Status field on the project board (https://github.com/users/snwiem/projects/7) is the **single source of truth** for workflow state. The allowed values and their meaning are:

| Status | Meaning |
|---|---|
| `Backlog` | Issue defined but not yet ready to start |
| `Ready` | Fully specified, can be picked up by an agent or developer |
| `In Progress` | Assigned and actively being worked on |
| `In Review` | PR is open and awaiting review |
| `Done` | PR merged, issue closed |

Always update the Status field when transitioning between states.

### Milestone

- All MVP issues must be assigned to the **MVP** milestone.
- Issues not targeted for MVP have no milestone assigned.

### Project Board Columns

| Column | Meaning |
|---|---|
| `Backlog` | Defined but not yet ready to start |
| `Ready` | Fully specified, can be picked up by an agent or developer |
| `In Progress` | Assigned and actively being worked on |
| `In Review` | PR open, awaiting review |
| `Done` | Merged and closed |

### Branch & PR Conventions

- Branch names must reference the issue number: `feature/42-short-description` or `fix/42-short-description`
- PR descriptions must contain `closes #<issue-number>` to auto-close the issue on merge.
- One issue = one branch = one PR.

### Parallel Agent Coordination

- Before starting work on an issue, an agent must:
  1. Assign itself to the issue.
  2. Move the issue to the `In Progress` column on the project board.
- This prevents two agents from picking up the same issue simultaneously.
- On opening a PR, move the board column to `In Review`.

# Refinement Sessions

When gathering or refining requirements with the user, follow these rules:

- **Ask questions one at a time.** Never bundle multiple questions into a single message.
- **Ask until aligned.** Keep asking follow-up questions until there is a clear, shared understanding of the requirement or decision at hand — do not assume or fill in gaps silently.
- **Write it down.** Once alignment is reached, immediately capture the outcome in the appropriate file (`docs/feature/` or `docs/adr/`) and commit it.
- **Don't jump ahead.** Do not start writing feature files or ADRs before the conversation has produced a clear and agreed-upon answer.

# Repository Structure

## docs/feature/

Contains feature and requirements definitions as simple Markdown files. Each file describes a single feature or requirement.

- **Naming convention:** `docs/feature/NNNN_short_description.md` (zero-padded 4-digit number, e.g. `0001_add_meter.md`)
- Files are written in plain Markdown and focus on *what* is needed, not *how* it is implemented.
- New features should always get a corresponding file here before implementation begins.

## docs/domain-concept.md

A single document describing the core domain objects, their meaning, attributes, and relationships. It is the authoritative reference for domain terminology used across feature files, ADRs, and source code. Keep it up to date as the domain model evolves.

## docs/adr/

Contains Architecture Decision Records (ADRs) — documents that capture significant design decisions that directly affect the architecture and source code.

- **Naming convention:** `docs/adr/NNNN_short_description.md` (zero-padded 4-digit number, e.g. `0001_choose_backend_framework.md`)
- Each ADR documents: the context, the decision made, and the consequences/rationale.
- ADRs are append-only: once recorded, existing ADRs should not be rewritten. Superseded decisions get a new ADR referencing the old one.


