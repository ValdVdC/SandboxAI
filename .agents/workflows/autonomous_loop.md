# Workflow: Autonomous Mission Execution

This workflow is triggered when the Human gives a high-level goal to @architect.

## Phase 1: Planning (@architect)
1. **Goal Analysis**: @architect reads the user request and project docs (`ROADMAP.md`, `ARCHITECTURE.md`).
2. **Blackboard Setup**: @architect updates `MISSION.md` with:
   - A clear technical strategy.
   - A list of sub-tasks assigned to specific agents.
3. **Approval**: @architect asks the Human: "Plan for [Goal] is ready in MISSION.md. Proceed?"

## Phase 2: Parallel Execution
1. **Trigger**: Once approved, @architect calls @backend-lead, @frontend-lead, and @qa-engineer simultaneously.
2. **Work**: Agents perform their tasks, updating `MISSION.md` as they finish.
3. **Sync**: If @frontend-lead needs an endpoint, they ask @backend-lead directly. @architect monitors these interactions.

## Phase 3: Integration & QA (@qa-engineer)
1. **Verification**: @qa-engineer runs tests on the merged code.
2. **Report**: @qa-engineer updates `MISSION.md` with test results.

## Phase 4: Closure (@architect)
1. **Review**: @architect performs a final audit of the code and docs.
2. **Delivery**: @architect notifies the Human: "Mission Accomplished. See MISSION.md for details."
