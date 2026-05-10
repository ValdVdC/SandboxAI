# 🛸 Antigravity Squad: SandboxAI — Operational Handbook

## 👥 Squad Members
- **@architect**: Lead Orchestrator. Responsible for Mission Planning, ADRs, and final code audit. Leads the mission planning.
- **@backend-lead**: FastAPI, SQLModel, Celery, and LLM Provider integrations.
- **@frontend-lead**: React, TypeScript, and UI/UX implementation.
- **@qa-engineer**: Testing (Pytest/Vitest), Docker environments, and CI/CD validation.

---

## 🏗️ 1. Shared Context & Technical Standards
1. **Source of Truth**: The primary documentation resides in `docs/` and `AGENTS.md`.
2. **Backend Standard**: Python 3.11+, PEP 8, Ruff for linting.
3. **Frontend Standard**: React 18+, TypeScript (strict mode), CSS variables for theming, Prettier for formatting.
4. **Dependency Management**: 
   - Backend: Add new libs to `backend/requirements.txt` with pinned versions.
   - Frontend: Use `npm install --save` to ensure `package.json` is updated.
5. **Environment Consistency (Docker-Only)**: Host-level installs (pip/npm) are allowed ONLY for IDE Intellisense. Official verification, testing, and execution MUST always happen inside Docker containers (e.g., via `docker compose up --build`).

---

## 🚦 2. Agent Protocols (The Loop)
1. **MISSION START**: @architect analyzes goal -> Updates `MISSION.md` with Technical Design and tasks.
2. **APPROVAL**: No agent starts coding until @architect approves the plan in `MISSION.md`.
3. **PARALLEL DEV**: @backend-lead & @frontend-lead work in sync.
   - **Backend**: Must include a migration (`backend/migrations/`) if models change.
   - **Frontend**: MUST sync with the `app/schemas/` definitions in the backend.
4. **STATUS UPDATES**: Agents MUST update their task status in `MISSION.md` after every successful sub-task.
5. **PEER REVIEW & QA**: @qa-engineer validates the implementation before mission closure.
6. **MISSION CLOSE (Mandatory Finality Check)**: 
   - @architect MUST run `git status` to ensure the branch is clean.
   - @architect MUST provide the commit hashes or PR link in the final message to the Human.
   - A mission is NOT closed until all code is committed and the status in `MISSION.md` is `Done`.

---

## 💾 3. Git Branching & PR Orchestration (Professional Workflow)
1. **Branch Hierarchy**:
   - `main`: Production-ready, stable code only.
   - `develop`: Integration branch. All features must be merged here first.
   - `feature/*`, `fix/*`, `refactor/*`: Isolated branches for specific tasks.
2. **The Lifecycle**:
   - **Start**: @architect creates a new branch from `develop` for the current mission.
   - **Work**: Agents commit atomic changes ONLY to the mission branch. Agents MUST `git push` to origin regularly to sync with the cloud.
   - **PR Preparation**: Once verified by @qa-engineer, @architect uses `gh pr create --base develop` to open the Pull Request.
   - **CI Monitoring**: @qa-engineer MUST use `gh pr checks` to monitor GitHub Actions status. If it fails, the squad must fix the code on the same branch.
   - **Merge**: A mission is only "Done" after Human approval and `gh pr merge --merge --delete-branch`.
3. **Atomic & Conventional Commits**:
   - Commits must be small, frequent, and follow Conventional Commits (feat, fix, etc.).
   - Use `git status` and `git diff` before every commit to ensure quality and security.

---

## 🛡️ 4. Operational Security & Integrity
1. **No Secrets Policy**: Never commit `.env` files. Always update `.env.example` when new environment variables are introduced.
2. **Self-Healing Protocol**: In case of failure, agents must attempt **3 rounds of autonomous diagnosis** (reading logs, checking configs) before escalating.
3. **Architecture Decision Records (ADR)**: Major technical shifts must be logged in `docs/decisions/`.

---

## ✅ 5. Definition of Done (DoD)
A task is only "Done" when:
- [ ] Code follows project style guides (Ruff/Prettier).
- [ ] Types are fully defined (no `Any` or `any`).
- [ ] At least one unit or integration test covers the change.
- [ ] Documentation is updated if behavior changes.
- [ ] A clean, verified commit is pushed to the repository.

---

## 📝 Mission Control
Current operational focus is maintained in `MISSION.md`. All agents MUST check the Mission blackboard before starting work.
