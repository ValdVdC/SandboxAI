# Mission: Human-in-the-loop: Sistema de Double Check

**Status**: Done
**Branch**: feature/human-in-the-loop

## Technical Design

A última grande Épica da Fase 2 do nosso Roadmap introduz o sistema "Human-in-the-loop", permitindo que um avaliador humano faça um double check e sobrescreva as avaliações de precisão dadas pela IA em resultados de testes.

### Decisões Arquiteturais Inegociáveis

1. **Data Model (Override Local)**:
   - Vamos adicionar uma coluna `is_human_overridden = Column(Boolean, default=False)` na tabela `TestResult`.
   - Quando o usuário humano discordar da nota de precisão da IA, o backend irá inverter o valor da coluna `is_correct` e setar `is_human_overridden = True`. 
   - Isso resolve o problema de auditoria sem precisar de tabelas separadas.

2. **Experiência do Usuário (UI)**:
   - Na nossa tabela de resultados de testes existente no Frontend (React), adicionaremos botões simples (👍 Aprovar / 👎 Reprovar).
   - Ao clicar, o frontend dispara a API e marca visualmente a linha com uma tag 'Override Manual'.

## Active Tasks

### @backend-lead
- [x] Adicionar o campo `is_human_overridden` no modelo `TestResult`.
- [x] Gerar e aplicar a migração (Alembic).
- [x] Criar o endpoint `PATCH /api/v1/tests/{test_id}/override` para inverter `is_correct` e marcar `is_human_overridden` como `True`.

### @frontend-lead
- [x] Modificar a interface de testes em lote.
- [x] Plugar os botões de Thumbs Up/Down consumindo o novo endpoint.
- [x] Marcar visualmente a linha atualizada com a tag 'Override Manual'.

### @architect
- [x] Iniciar a branch `feature/human-in-the-loop` a partir da `develop`.
- [x] Elaborar o Technical Design no `MISSION.md` detalhando as duas decisões de arquitetura e montar as Active Tasks para o squad.
- [x] Validar a implementação, realizar o PR via `gh pr create` e garantir que o `gh pr checks` passe 100% verde antes de fechar a missão.
