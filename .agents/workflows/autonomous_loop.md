# Workflow: Autonomous Mission Execution (Gitflow Version)

This workflow is triggered when the Human gives a high-level goal to @architect.

## Phase 1: Planning & Branching (@architect)
1. **Goal Analysis**: @architect reads the user request and project docs (`ROADMAP.md`, `ARCHITECTURE.md`).
2. **Branching**: @architect creates a new `feature/*` or `fix/*` branch from `develop`.
3. **Blackboard Setup**: @architect updates `MISSION.md` with:
   - A clear technical strategy.
   - A list of sub-tasks assigned to specific agents.
4. **Approval**: @architect asks the Human: "Plan for [Goal] is ready in MISSION.md on branch [name]. Proceed?"

## Phase 2: Parallel Execution
1. **Trigger**: Once approved, @architect calls @backend-lead, @frontend-lead, and @qa-engineer.
2. **Work**: Agents perform their tasks, committing ONLY to the mission branch.
3. **Sync**: If @frontend-lead needs an endpoint, they ask @backend-lead directly. @architect monitors these interactions to ensure schema alignment.
4. **Update**: Agents update `MISSION.md` after every successful atomic commit.

## Phase 3: Integration & PR Prep (@qa-engineer & @architect)
1. **Verification**: @qa-engineer runs tests on the mission branch.
2. **DoD Check**: @qa-engineer confirms the Definition of Done is met.
3. **PR Prep**: @architect performs a final audit and prepares the branch for a Pull Request to `develop`.

## Phase 4: Closure & Delivery (@architect)
1. **Final Review**: @architect records major choices in ADRs (`docs/decisions/`).
2. **Human Handoff**: @architect notifies the Human: "Mission Accomplished on [branch]. Ready for PR to develop."
3. **Merge**: After Human approval/PR merge, the mission is officially closed.
