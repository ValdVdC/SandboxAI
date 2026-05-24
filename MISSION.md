# Mission: Integração CI/CD (DevOps)

**Status**: Done
**Branch**: feature/ci-cd-prompt-testing

## Technical Design

A missão épica de Integração CI/CD visa garantir a estabilidade e a eficiência dos prompts através de testes contínuos automatizados.

### Decisões Arquiteturais Inegociáveis

1. **Trigger Engine (Cliente CLI)**:
   - O script CLI Python será apenas um cliente burro.
   - Ele deve ler um arquivo local chamado `sandboxai-ci.yml` na raiz do repositório onde a GitHub Action rodar. Este arquivo especificará os IDs dos prompts alvo que devem ser testados.
   - Em caso de falha (status FAIL), a CLI deve imprimir o texto de justificativa retornado pelo backend e forçar um `exit 1` para quebrar a pipeline CI/CD.

2. **Rule Engine (Server-side)**:
   - Toda a inteligência de avaliação (ex: custo explodindo em >20% ou precisão semântica caindo) ocorrerá no Backend do SandboxAI.
   - O endpoint avaliará o histórico de execução e calculará o drift.
   - O endpoint retornará um status consolidado (`PASS` ou `FAIL`) junto com a justificativa detalhada em texto.

## Active Tasks

### @backend-lead
- [x] Criar o script CLI em Python (na pasta `backend/scripts/`) utilizando as bibliotecas padrão ou `argparse`/`typer`.
- [x] Criar/atualizar o endpoint da API para calcular o drift (regressão de custos e precisão) com base no histórico, retornando o status final e justificativa.

### @qa-engineer
- [x] Criar a documentação do processo de CI/CD para os usuários.
- [x] Criar um template real `.github/workflows/sandboxai-test-template.yml` para os clientes copiarem em seus repositórios.

### @architect
- [x] Iniciar a branch `feature/ci-cd-prompt-testing` a partir da `develop`.
- [x] Elaborar o Technical Design no `MISSION.md` definindo as regras da Trigger Engine e Rule Engine.
- [x] Validar a implementação, realizar o PR via `gh pr create` e garantir que o `gh pr checks` passe 100% verde antes de fechar a missão.
