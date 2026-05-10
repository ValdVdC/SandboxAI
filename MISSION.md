# 🎯 Mission: Gestão Dinâmica de Datasets (Upload de CSV/JSON para testes em lote)

*Status: Done - Mission Completed.*

---

## 🏛️ Architect's Vision
*Objective: Implementar upload de arquivos CSV/JSON com múltiplas variáveis para popular prompt templates via Jinja2 no Bulk Testing.*

### Proposed Strategy
1. [ ] Atualizar o Worker (`tasks.py`) para renderizar os prompts usando `jinja2` e aceitar inputs em formato JSON para lidar com múltiplas variáveis dinâmicas.
2. [ ] Adicionar dependências `python-multipart`, `jinja2` e `pandas` (ou nativo) ao backend.
3. [ ] Criar um novo endpoint no backend (`POST /api/v1/prompt-versions/{version_id}/test/bulk/upload`) para processar arquivos `.csv` e `.json`.
4. [ ] Extrair dinamicamente a coluna `expected` (se existir) dos datasets para uso na avaliação semântica.
5. [ ] No Frontend, adicionar uma aba de "Upload Dataset" no modal de Bulk Testing com parsing preview (usando `papaparse` para CSV) e submissão via `FormData`.

---

## 📋 Active Tasks
- [x] @architect: Definição da missão, branch criada (`feature/dynamic-datasets-upload`), plano de implementação aprovado pelo humano.
- [x] @backend-lead: Implementar renderização Jinja2 no `tasks.py` e novo endpoint de upload. Adicionar dependências.
- [x] @frontend-lead: Adicionar lib `papaparse` e implementar nova UI de upload no modal de Bulk Testing.
- [x] @qa-engineer: Adicionar testes unitários para a rota de upload e renderização Jinja2. Realizar testes end-to-end do fluxo no Frontend.

## 🚧 Blockers
- None.

## 📝 Recent Decisions
- Nova branch `feature/dynamic-datasets-upload` criada a partir de `develop`.
- A engine de templates de prompts passa a ser Jinja2 no backend.
- A coluna com nome `expected` no CSV/JSON enviado será mapeada como a "Expected Output" para a validação semântica. O restante das colunas será tratado como variáveis dinâmicas do prompt.
