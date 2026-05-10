# Mission: Semantic Similarity Validation & AI Squad Setup

## Architect's Vision: Semantic Similarity Validation

_Objective: Go beyond exact matches. Use embeddings to verify if an LLM output means the same thing as the expected value._

### Proposed Strategy

1. **Embedding Service**: Implement a utility in `backend/app/services/embeddings.py` using `sentence-transformers` (local) or OpenAI Embeddings (cloud).
2. **Worker Integration**: Update `backend/app/workers/tasks.py` to calculate cosine similarity when `expected` is provided and simple match fails.
3. **DB Update**: We already have the `score` column (added in migration 005). We will use it to store the similarity value (0.0 to 1.0).
4. **Thresholds**: Allow users to set a `similarity_threshold` per test (default 0.8).

---

## Active Tasks

- [x] @architect: Setup Antigravity Squad configuration (`AGENTS.md`, `.agents/`).
- [ ] @backend-lead: Implementar cálculo de embeddings usando `fastembed` (recomendado por rodar via ONNX sem impacto pesado na CPU/RAM).
- [ ] @frontend-lead: Update `TestResults.tsx` to display the similarity score as a percentage when available.
- [ ] @qa-engineer: Create a benchmark test suite with synonymous inputs to validate the semantic engine.

## Blockers

- Nenhuma infraestrutura pesada necessária se adotarmos `fastembed` em vez de bibliotecas dependentes do PyTorch.

## Recent Decisions

- 2026-05-09: Reorganized migrations to `backend/migrations/` for better clarity.
- 2026-05-09: Implemented basic "Contains" validation as a fallback.
