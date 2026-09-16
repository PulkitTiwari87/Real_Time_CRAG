# Agents Overview

## User
- Provides requirements, reviews plans, approves changes.

## Antigravity (this agent)
- Responsible for planning, auditing, creating documentation, and committing changes.
- Must never modify implementation files directly.

## Claude Code
- Executes implementation tasks, runs tests, generates evaluation results, and produces documentation.
- **Cannot** create Git commits, push, or modify planning artifacts.

## GitHub (remote)
- Stores the repository. Commits are only created by Antigravity.

Each agent's permissions are enforced by the workflow:
```
TARGET → INSPECT → IMPLEMENT → TEST → VERIFY → ANTIGRAVITY AUDIT → ANTIGRAVITY COMMIT
```
