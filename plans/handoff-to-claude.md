# Handoff to Claude Code

**Purpose**: Define the exact deliverables and expectations for Claude Code when it begins Phase 01 implementation.

1. **Scope**: Claude Code may only work on implementation files (e.g., code under `src/`, configuration scripts, test suites). It must not modify any planning, documentation, or ADR files.
2. **Artifacts to Produce**:
   - Implement the foundation scaffold (basic package structure, `src/__init__.py`).
   - Add initial unit test placeholder under `tests/`.
   - Update `requirements.txt` with runtime dependencies needed for Phase 00.
3. **Verification**: After completing its tasks, Claude Code must produce a short report summarizing:
   - Files created/modified.
   - Any test results.
   - Any open questions for Antigravity.
4. **Constraints**:
   - No Git commits or pushes.
   - No network calls to paid services.
   - Must respect free‑LLM token budget.
5. **Handoff Checklist**:
   - [ ] All planning artifacts are present and approved.
   - [ ] `requirements-dev.txt` includes linting and test tools.
   - [ ] Token‑budget middleware stub is added (no implementation yet).
   - [ ] Documentation files are untouched.

Claude Code should begin work only after receiving explicit approval to start Phase 01.
