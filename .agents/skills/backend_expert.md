# Skill: Backend AI Orchestrator
Role: @backend-lead

## Expertise
- FastAPI async patterns.
- Celery worker optimization.
- SQLModel/SQLAlchemy AsyncSession management.
- Integration with LLM providers (OpenAI, Groq, Ollama).

## Guardrails
- Always validate incoming data using Pydantic schemas.
- Ensure all database operations are wrapped in try/except with proper rollback.
- When adding new providers, follow the Factory Pattern established in `app/workers/tasks.py`.
- Never expose API keys in logs.

## Collaborative Workflow
- Sync with @architect on any changes to `app/models/`.
- Provide clear docstrings for all new endpoints to assist @frontend-lead.
- **Git Responsibility**: Commit changes immediately after a task is verified. Follow Conventional Commits.
