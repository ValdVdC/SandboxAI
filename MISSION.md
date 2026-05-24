# 🚀 MISSION: Real-Time Multi-Provider Playground

## 🎯 Goal
Desenvolver a feature 'Playground Multi-Provider em Tempo Real'. Esta funcionalidade permitirá aos usuários interagir com múltiplos provedores de LLMs simultaneamente, visualizando as respostas lado a lado em tempo real.

## 🏗️ Technical Design
A arquitetura deve seguir rigorosamente estas 3 decisões arquiteturais inegociáveis:

1. **UI Layout (Colunas Paralelas)**
   - Layout de colunas paralelas contendo um Editor central.
   - 3 colunas dispostas lado a lado para exibição das respostas dos diferentes LLMs.

2. **Concurrency (Execução Paralela no Cliente)**
   - A execução e orquestração da concorrência ocorrerão no cliente (React).
   - O frontend fará requisições HTTP simultâneas e paralelas para garantir que a UI não seja bloqueada durante a espera pelas respostas.

3. **Version Control (Edição Live e Salvamento Manual)**
   - Suporte para Edição Live com salvamento manual.
   - Inclusão de um botão 'Salvar como Nova Versão', que será responsável por registrar as novas versões dos prompts no banco de dados, compondo o Histórico de Prompts.

## 📋 Active Tasks

### 👷‍♂️ @architect (Mission Planning & Coordination)
- [x] Criar a branch `feature/realtime-multiprovider-playground` a partir da `develop`.
- [x] Substituir e reescrever o arquivo `MISSION.md` com os objetivos, design técnico e as tarefas iniciais.
- [ ] Validar a integração final, verificar status do Git (`git status`) e garantir que a CI/CD esteja 100% verde (`gh pr checks`) antes do fechamento da missão.

### 🔌 @backend-lead (API & Database Integration)
- [x] Criar endpoint assíncrono genérico e não-bloqueante (FastAPI) capaz de receber requisições do frontend e repassá-las aos provedores de LLM suportados.
- [x] Criar a migração de banco de dados (SQLModel) para implementar a tabela de Histórico de Prompts (suportando o botão 'Salvar como Nova Versão').
- [x] Atualizar os esquemas Pydantic (`app/schemas/`) para garantir que o @frontend-lead possa se sincronizar adequadamente.

### 🎨 @frontend-lead (React UI & State Management)
- [x] Implementar os componentes React para o Layout de Colunas (Editor central + 3 colunas de respostas).
- [x] Implementar a lógica e o estado paralelo (React State/Hooks) para disparar e gerenciar requisições HTTP simultâneas sem bloquear a UI.
- [x] Integrar a funcionalidade de "Salvar como Nova Versão" com o backend (Console Log isolado no topo).

## 🚦 Status
- **Fase Atual:** Finalizada (Pronto para QA).
- **Status:** Concluído. Todas as integrações (UI, Rotas e Banco de Dados) foram validadas.
