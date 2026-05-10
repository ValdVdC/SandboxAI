# Antigravity Squad: SandboxAI

## Squad Members

- **@architect**: System design, DB schemas, and high-level orchestration. Leads the mission planning.
- **@backend-lead**: FastAPI, SQLModel, Celery, and LLM Provider integrations.
- **@frontend-lead**: React, TypeScript, and UI/UX implementation.
- **@qa-engineer**: Testing (Pytest/Vitest), Docker environments, and CI/CD validation.

## Shared Context & Constraints

1. **Source of Truth**: The primary documentation resides in `docs/` and `AGENTS.md`.
2. **Development Standard**:
   - Backend: Python 3.11+, PEP 8, Ruff for linting.
   - Frontend: React 18+, TypeScript (strict mode), CSS variables for theming.
3. **Branching & Commits**: 
   - Conventional Commits only (feat, fix, docs, refactor, etc.).
   - **Autonomous Commits**: Agents MUST commit their changes as soon as a sub-task is completed and verified. 
   - Each commit should be atomic (focus on one task/fix).
   - Use `git status` and `git diff` before committing to ensure no unintended changes are included.
4. **Agent Protocol**: 
   - Before coding, @architect must approve the implementation plan in `MISSION.md`.
   - After a successful commit, the agent MUST update the status in `MISSION.md`.
   - Backend updates must include a migration if models change.
## Mission Control

Current operational focus is maintained in `MISSION.md`. All agents MUST check the Mission blackboard before starting work.
