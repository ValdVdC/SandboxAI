# 🎯 Mission: Avaliação por similaridade semântica (NLP) via Embeddings

*Status: Done - Mission Completed.*

---

## 🏛️ Architect's Vision
*Objective: Implementar validação semântica baseada em similaridade de embeddings (Fase 2 do Roadmap) para testes do SandboxAI, substituindo a verificação de "exact match".*

### Proposed Strategy
1. [x] Adicionar dependências `fastembed` e `numpy` ao backend.
2. [x] Instanciar o modelo de embedding no escopo dos workers do Celery para evitar carregamento repetitivo.
3. [x] Substituir a lógica de validação (`is_correct` e `score`) em `_execute_test_async` para usar Cosine Similarity entre a saída real e a esperada.
4. [x] Garantir que o valor fracionado do score (0.0 a 1.0) seja salvo corretamente no banco de dados.
5. [x] Escrever/atualizar testes unitários para a nova lógica de avaliação.

---

## 📋 Active Tasks
- [x] @architect: Define the mission and sub-tasks, created implementation plan.
- [x] @backend-lead: Implementar lógica de `fastembed` no `tasks.py` e atualizar `requirements.txt`.
- [x] @frontend-lead: N/A (Frontend já exibe o score corretamente como definido nos schemas).
- [x] @qa-engineer: Adicionar/atualizar testes de validação semântica.

## 🚧 Blockers
- None.

## 📝 Recent Decisions
- Nova branch `feature/semantic-validation` criada.
- Optamos pelo uso da biblioteca `fastembed` por ser leve e rodar offline.
- Threshold de similaridade configurável via `.env` (default: 0.8).
- Modelo escolhido: `intfloat/multilingual-e5-small`.
