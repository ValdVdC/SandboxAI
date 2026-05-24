# 🗺️ Roadmap — SandboxAI

Este documento descreve o planejamento de desenvolvimento do SandboxAI, organizado em fases.

---

## Metodologia de Desenvolvimento (Antigravity Squad)
O SandboxAI é desenvolvido utilizando um paradigma "Agent-First". A orquestração Multi-Agente (AGENTS.md, MISSION.md) **não é uma funcionalidade do produto final**, mas sim a estrutura de times virtuais (`@architect`, `@backend-lead`, `@frontend-lead`, `@qa-engineer`) que constrói o código.

---

## Fase 1 — MVP Acadêmico (Concluída)

Objetivo: entregar uma versão funcional para o seminário de Tópicos Integradores.

- [x] Documentação completa do projeto
- [x] Estrutura base do Docker Compose
- [x] API com endpoints de CRUD de prompts
- [x] Versionamento básico de prompts
- [x] Integração com Ollama (local)
- [x] Integração com Groq
- [x] Registro de métricas básicas (latência, tokens, custo)
- [x] Frontend funcional para criar e testar prompts
- [x] Autenticação completa com JWT (User login/register)
- [x] Integração com OpenAI e Anthropic (Backend)
- [x] Dashboard básico de métricas e custos

---

## Fase 2 — Produto: Consolidação & Testes Avançados (Em andamento)

Objetivo: evoluir para um produto utilizável por engenheiros de IA e DevOps.

- [x] Comparação side-by-side de versões (Visual Diff)
- [x] Baterias de testes automatizados (Bulk Testing) com limitação de quotas
- [x] Dashboard de Analytics Avançado (Trend lines e Confiabilidade)
- [x] Exportação de resultados (CSV/JSON)
- [x] Documentação da API pública (Swagger/Redoc)
- [ ] **Framework de Validação Inteligente:**
    - [x] Validação automática básica (Exact/Contains match)
    - [x] Avaliação por similaridade semântica (NLP) via Embeddings
    - [ ] Human-in-the-loop: Sistema de "Double Check" manual para calibrar validações automáticas
- [x] **Gestão Dinâmica de Datasets:**
    - [x] Upload de CSV/JSON com centenas de variáveis para testes em lote
- [x] **Playground Multi-Provider em Tempo Real:**
    - [x] Interface com múltiplas colunas para rodar 1 prompt em 3 modelos simultaneamente (A/B/C testing)
- [ ] **Integração CI/CD (DevOps):**
    - [ ] CLI/GitHub Action do SandboxAI para rodar "Prompt Unit Tests" no Pull Request
    - [ ] Trava de CI/CD: falhar build se o custo de um prompt aumentar >20% ou a precisão cair

---

## Fase 3 — SaaS & Observabilidade

Objetivo: transformar em um serviço corporativo escalável, monetizável e seguro.

- [ ] **Observabilidade Avançada:**
    - [ ] Implementação de Semantic Caching (Redis) para economizar tokens em testes repetidos
    - [ ] Tracing com OpenTelemetry (Gargalos de rede vs latência de IA)
- [ ] **Gestão de Infraestrutura:**
    - [ ] Sandbox Real (Docker-in-Docker para isolamento total da rede)
    - [ ] Gestão de Conta (Workspaces Multi-tenant para times)
    - [ ] Quotas financeiras rigorosas e Circuit Breakers por usuário/organização
- [ ] **Ecossistema:**
    - [ ] Sistema de planos (Free, Pro, Teams)
    - [ ] Compartilhamento de prompts entre usuários (Template Hub)
    - [ ] Webhooks para notificações externas (ex: Slack quando um teste em lote termina)
    - [ ] Integração nativa bidirecional com GitHub (sincronizar prompts com repositórios)
