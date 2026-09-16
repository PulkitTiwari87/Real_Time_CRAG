# Phase 00 – Foundation

## Objective
Create the repository scaffolding, documentation, and planning artifacts required for the project.

## Why it exists
Establish a solid, provider‑agnostic baseline before any implementation code is added.

## Prerequisites
- Git repository initialized.
- No existing implementation files.

## Concepts to learn
- Repository layout conventions.
- Markdown documentation standards.
- Free‑LLM token budgeting basics.

## In‑scope work
- Create top‑level directories (`src/`, `data/`, `tests/`, `scripts/`, `infrastructure/`).
- Add placeholder `README.md` files in each.
- Populate planning files (`PROJECT.md`, `DECISIONS.md`, `CONTRIBUTING.md`, `SECURITY.md`, `CLAUDE.md`, `AGENTS.md`).
- Generate `requirements.txt` and `requirements-dev.txt`.
- Add `.gitignore` and `.env.example`.
- Create `plans/roadmap.md`, `plans/execution-rules.md`, `plans/handoff-to-claude.md`.
- Add ADRs 001‑010.
- Create docs folders (`docs/evaluation/`, `docs/token_strategy/`, `docs/experiments/`).

## Explicit non‑scope
- No implementation of retrieval, embedding, or generation logic.
- No CI/CD pipelines.
- No Dockerfiles or deployment scripts.

## Expected files
- All files listed above plus placeholder README files for each new directory.

## Implementation tasks
1. Run directory creation commands (already done).
2. Write each documentation file with the required sections.
3. Verify file presence and content.

## Tests
- None (documentation‑only phase).

## Evaluation / Metrics
- Verify that every required file exists.
- Check that no implementation code is present.

## Risks / Failure cases
- Accidentally adding code files.
- Missing required documentation sections.

## Acceptance criteria
- All files listed in the bootstrap requirements are present.
- No implementation source code files exist.
- All documentation follows the template.

## Definition of Done
- Files created and verified.
- Git status shows only these new files as untracked or modified.
- No planning artifacts duplicated.

## Handoff requirements
- Claude Code may start Phase 01 after receiving explicit approval.
