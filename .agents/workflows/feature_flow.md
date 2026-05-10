# Workflow: Feature Implementation Cycle

## Stage 1: Design (@architect)
- Update `MISSION.md` with the feature requirements.
- Define DB schema changes and API endpoints.

## Stage 2: Development (@backend-lead & @frontend-lead)
- @backend-lead implements the logic and migrations.
- @frontend-lead implements the UI based on backend schemas.
- Continuous sync via `MISSION.md` status updates.

## Stage 3: Validation (@qa-engineer)
- Write integration tests.
- Verify Docker-compose build consistency.
- Perform manual UI testing of the new feature.

## Stage 4: Review (@architect)
- Final code review.
- Update `ROADMAP.md` and `CHANGELOG.md`.
