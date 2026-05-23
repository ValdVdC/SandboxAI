# 🎯 Mission: CI/CD and Governance Hardening (Blindagem da Infraestrutura de CI/CD e Governança)

*Status: In Progress - Awaiting CI/CD Verification.*

---

## 🏛️ Architect's Vision
*Objective: Solidificar a governança do squad e blindar a infraestrutura de CI/CD de forma definitiva, assegurando que atualizações de dependências ocorram de forma automatizada e segura (Dependabot), que revisões por IA de PRs sejam de fácil ativação (CodeRabbit), e que nenhuma entrega ao Humano ocorra sem a validação verde total de workflows via GitHub CLI (`gh pr checks`).*

### Technical Design & Strategy
1. **Dependabot Configuration**: 
   - Arquivo `.github/dependabot.yml` configurado na versão `2`.
   - Monitoramento semanal de atualizações de dependências:
     - Backend (`pip` em `/backend`)
     - Frontend (`npm` em `/frontend`)
     - Dockerfiles e compose files (`docker` em `/backend`, `/frontend`, e `/`)
2. **CodeRabbit Integration Guide**:
   - Criação do documento `docs/CODERABBIT.md` de fácil leitura para o time.
   - Detalhamento passo-a-passo simples para ativação no link `app.coderabbit.ai/wizard`.
3. **Hardening of Squad Rules (`AGENTS.md`)**:
   - Modificação da etapa **6. MISSION CLOSE (Mandatory Finality Check)** em `AGENTS.md` para exigir explicitamente que toda missão ou Pull Request só seja finalizada após o `@architect` rodar o comando `gh pr checks` e anexar o checklist 100% verde no relatório ao Humano.
   - Atualização do **Definition of Done (DoD)** para garantir que "Toda verificação de CI via `gh pr checks` está verde e validada pelo `@architect`".

---

## 📋 Active Tasks
- [x] **@architect**: Definição da missão, criação da branch (`feature/ci-cd-and-governance-hardening`) e Technical Design no `MISSION.md` (Aprovado).
- [x] **@architect**: Criação do arquivo `.github/dependabot.yml`.
- [x] **@architect**: Criação do guia de integração do CodeRabbit (`docs/CODERABBIT.md`).
- [x] **@architect**: Atualização das regras do squad no `AGENTS.md`.
- [x] **@qa-engineer**: Validação do YAML de dependabot, revisão de conformidade geral e garantia do DoD.
- [/] **@architect**: Revisão de código final, execução de `gh pr checks`, e preparação da mensagem de encerramento da missão com o checklist 100% verde e link da PR.

---

## 🚧 Blockers
- None.

---

## 📝 Recent Decisions
- Centralizar o monitoramento do Dependabot de forma semanal, garantindo atualizações regulares sem sobrecarregar o fluxo de desenvolvimento do time.
