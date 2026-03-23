# 📝 Changelog — SandboxAI

Todas as mudanças notáveis deste projeto serão documentadas aqui.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.0.0/), e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

---

## [Não lançado]

### Adicionado

#### Frontend (React + TypeScript)
- Interface completa em React 18.2.0 com TypeScript 5.3.3
- Sistema de autenticação JWT com login e registro
- Dashboard com listagem de prompts
- Página de detalhes de prompt com versionamento
- Componente PromptEditor para edição de prompts
- Componente VersionList com seleção de versões
- Componente CreateVersion para criar novas versões com descrição de mudanças
- Componente TestRunner para executar testes em prompts
- Componente TestResults para exibir resultados de testes
- Componente TestHistory para listar histórico de testes por versão
- Componente VersionComparison para comparar versões
- Sistema completo de roteamento protegido com PrivateRoute
- AuthContext para gerenciamento global de autenticação
- Dark theme com CSS semântico usando variáveis CSS
- Integração com API REST via axios com interceptadores JWT
- LocalStorage para persistência de tokens e dados de usuário
- Suporte a refresh automático de histórico de versões

#### Backend (FastAPI + SQLAlchemy)
- API REST completa com FastAPI
- Autenticação JWT com geração e validação de tokens
- Endpoints CRUD para prompts e versions
- Endpoints para execução de testes via Celery
- Sistema de paginação nas listagens
- Schemas Pydantic com validação de dados
- Models SQLAlchemy para Users, Prompts, PromptVersions, e TestResults
- Suporte a PostgreSQL com async driver (asyncpg)
- CORS configurado para aceitar requisições do frontend
- Health check endpoint (`/health`)
- Documentação automática via Swagger (`/docs`)

#### Database & Migrations
- PostgreSQL 15 como banco de dados principal
- Alembic para controle de migrações de schema
- Migração inicial 001_initial criando tabelas base (users, prompts, prompt_versions, test_results)
- Migração 002_add_change_description para adicionar rastreamento de mudanças nas versões
- Script programático `run_migrations.py` para executar migrações sem usar CLI
- Função `init_db()` para inicializar schema do banco de dados

#### Infrastructure & DevOps
- Docker multi-stage build para otimizar tamanho da imagem
- Docker Compose orquestrando 7 serviços: PostgreSQL, Redis, Ollama, FastAPI, Celery Worker, Frontend, e integração com HTTPS
- Script `entrypoint.sh` para orquestrar inicialização de migrações e servidor FastAPI
- Variáveis de ambiente para configuração (DATABASE_URL, JWT_SECRET, etc)
- Health checks para todos os serviços
- Persistent volumes para PostgreSQL, Redis e Ollama
- Network isolada para comunicação entre containers

#### Task Queue & Caching
- Redis 7 como message broker
- Celery 5.3.4 para processamento assíncrono de testes
- Background workers para execução de testes sem bloquear API

#### Documentation
- README.md com instruções de setup e uso
- ARCHITECTURE.md documentando estrutura do projeto
- ENVIRONMENT.md com variáveis de ambiente necessárias
- REQUIREMENTS.md listando dependências
- CONTRIBUTING.md com guidelines para contribuição
- SECURITY.md com boas práticas de segurança
- ROADMAP.md com plano de desenvolvimento futuro

#### Validação & Business Logic
- Validação de compatibilidade provider/model (opsional seleção de modelos por provider)
- Cálculo de custo em USD para execução de testes
- Rastreamento de tempo de execução (latency_ms)
- Contagem de tokens consumidos
- Status de resultado de teste (pending, success, failed)
- Controle de acesso: usuários só veem seus próprios prompts

### Modificado
- Renderização de "Descrição da Mudança" agora aparece apenas quando houver conteúdo (antes mostrava "Sem descrição" para debug)
- Seleção automática de versão no PromptDetail: agora seleciona a ÚLTIMA versão em vez de v1
- Atualização imediata do histórico de versões após criar nova versão (sem necessidade de recarregar página)
- Register form: rótulo de campo "Usuário" mudado para "Nome Completo" (full_name)

### Corrigido
- Conflito de namespace do módulo Alembic no Docker ao importar `from alembic import command` (sys.path.insert para priorizar venv)
- Autenticação no Register: campo enviado para backend era `username`, corrigido para `full_name`
- Função `run_migrations_online()` NO `alembic/env.py`: removeu await desnecessário que causava erro "NoneType can't be used in 'await'"
- Removido `command` do docker-compose.yml que sobrescrevia `CMD` do Dockerfile (migrações não executavam)
- Erro de DuplicateTable ao tentar criar tabelas que já existiam (alembic_version não rastreava migrações anteriores)
- Renderização de custo USD em decimal não funcionava (parseFloat wrapper adicionado)
- Novos prompts não apareciam na lista sem recarregar página (localStorage flag adicionado)
- Mensagens de erro de autenticação inválida (422 Unprocessable Entity, 401 Unauthorized) agora com validação clara

### Removido
- Console.logs de debug em PromptDetail.tsx
- Console.logs de debug em VersionList.tsx
- Visual de debug "Sem descrição (ver console)" que aparecia para v1

---

## Guia de Versionamento

| Versão | Quando usar |
|--------|-------------|
| `MAJOR` (1.x.x → 2.0.0) | Mudanças incompatíveis com versões anteriores |
| `MINOR` (1.0.x → 1.1.0) | Nova funcionalidade compatível com versão anterior |
| `PATCH` (1.0.0 → 1.0.1) | Correção de bug compatível com versão anterior |

### Categorias de mudança

- **Adicionado** — novas funcionalidades
- **Modificado** — mudanças em funcionalidades existentes
- **Descontinuado** — funcionalidades que serão removidas em breve
- **Removido** — funcionalidades removidas
- **Corrigido** — correções de bugs
- **Segurança** — correções de vulnerabilidades
