# 🏗️ Arquitetura Técnica — SandboxAI

## Visão Geral

O SandboxAI é composto por cinco serviços independentes que se comunicam entre si, todos orquestrados via Docker Compose. Cada serviço tem responsabilidade única e pode ser escalado de forma independente.

---

## Diagrama de Arquitetura

```
                        ┌─────────────────────────────────────────────┐
                        │              Docker Network                 │
                        │                                             │
  Usuário ──HTTP──▶ ┌───┴──────┐    ┌──────────┐    ┌─────────────┐ │
                    │ Frontend │───▶│   API    │───▶│    Redis    │ │
                    │  :3000   │    │  :8000   │    │   :6379     │ │
                    └──────────┘    └────┬─────┘    └──────┬──────┘ │
                                        │                  │        │
                                   ┌────▼─────┐    ┌───────▼──────┐ │
                                   │ Postgres │    │    Worker    │ │
                                   │  :5432   │    │  (Executor)  │ │
                                   └──────────┘    └───────┬──────┘ │
                                                           │        │
                                                   ┌───────▼──────┐ │
                                                   │   Ollama     │ │
                                                   │  :11434      │ │
                                                   └──────────────┘ │
                        └─────────────────────────────────────────────┘
```

---

## Serviços

### 1. Frontend (React + TypeScript)

Responsável pela interface do usuário. Consome a API REST do backend.

```yaml
frontend:
  build: ./frontend
  ports:
    - "3000:3000"
  environment:
    - VITE_API_URL=http://api:8000
  depends_on:
    - api
```

**Responsabilidades:**
- Interface para criação e versionamento de prompts
- Visualização de resultados e métricas
- Comparação side-by-side de versões
- Dashboard de uso e custos

---

### 2. API (Python + FastAPI)

Núcleo da aplicação. Expõe os endpoints REST e coordena os demais serviços.

```yaml
api:
  build: ./backend
  ports:
    - "8000:8000"
  environment:
    - DATABASE_URL=postgresql://user:pass@postgres:5432/sandboxai
    - REDIS_URL=redis://redis:6379
  depends_on:
    - postgres
    - redis
```

**Responsabilidades:**
- Autenticação e autorização
- CRUD de prompts e versões
- Enfileiramento de testes no Redis
- Agregação de métricas

**Endpoints principais:**

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/prompts` | Criar novo prompt |
| GET | `/prompts` | Listar prompts |
| GET | `/prompts/{id}` | Detalhar prompt |
| POST | `/prompts/{id}/versions` | Nova versão |
| POST | `/prompts/{id}/test` | Executar teste |
| GET | `/prompts/{id}/results` | Resultados dos testes |
| GET | `/metrics` | Métricas de uso |

---

### 3. Worker (Python + Celery)

Responsável pela execução isolada dos testes de prompts. Cada teste é executado em um container Docker dedicado.

```yaml
worker:
  build: ./backend
  command: celery -A app.worker worker
  volumes:
    - /var/run/docker.sock:/var/run/docker.sock
  depends_on:
    - redis
    - postgres
```

**Responsabilidades:**
- Consumir fila de testes do Redis
- Criar containers Docker isolados por teste
- Chamar providers de LLM (Groq, OpenAI, Ollama)
- Destruir containers após execução
- Persistir resultados e métricas no banco

**Fluxo de execução de um teste:**

```
Redis Queue
    │
    ▼
Worker recebe tarefa
    │
    ▼
Cria container Docker isolado
    │
    ▼
Injeta prompt + variáveis
    │
    ▼
Chama provider LLM
    │
    ▼
Coleta resultado + métricas
    │
    ▼
Destrói container
    │
    ▼
Persiste no PostgreSQL
```

---

### 4. PostgreSQL

Banco de dados relacional principal. Armazena todos os dados persistentes da aplicação.

**Schema principal:**

```sql
-- Usuários
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Prompts
CREATE TABLE prompts (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    name VARCHAR NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Versões de prompts
CREATE TABLE prompt_versions (
    id UUID PRIMARY KEY,
    prompt_id UUID REFERENCES prompts(id),
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    provider VARCHAR NOT NULL,
    model VARCHAR NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Resultados de testes
CREATE TABLE test_results (
    id UUID PRIMARY KEY,
    version_id UUID REFERENCES prompt_versions(id),
    input TEXT NOT NULL,
    output TEXT,
    expected TEXT,
    latency_ms INTEGER,
    tokens_used INTEGER,
    cost_usd DECIMAL(10,6),
    status VARCHAR,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 5. Redis

Fila de mensagens para comunicação assíncrona entre API e Worker.

```yaml
redis:
  image: redis:7-alpine
  ports:
    - "6379:6379"
```

**Responsabilidades:**
- Fila de execução de testes
- Cache de resultados frequentes
- Controle de rate limiting por usuário

---

### 6. Ollama (opcional)

Servidor local de LLMs. Permite executar modelos de IA completamente offline.

```yaml
ollama:
  image: ollama/ollama
  ports:
    - "11434:11434"
  volumes:
    - ollama_data:/root/.ollama
```

**Modelos suportados:**
- `llama3:8b` — uso geral, equilibrado
- `mistral:7b` — rápido e eficiente
- `gemma:7b` — bom para tarefas estruturadas
- `phi3:mini` — muito leve, ideal para testes rápidos

---

## Providers de LLM suportados

| Provider | Requer API Key | Custo | Indicado para |
|----------|---------------|-------|---------------|
| Ollama | Não | Gratuito | Desenvolvimento local |
| Groq | Sim (gratuito) | Gratuito | Testes e demos |
| OpenAI | Sim (pago) | Por token | Produção |
| Anthropic | Sim (pago) | Por token | Produção |

---

## Decisões de Arquitetura

### Por que Docker para cada teste?

Cada teste de prompt roda em um container isolado para garantir:
- **Reprodutibilidade** — mesmo ambiente sempre
- **Isolamento** — falha em um teste não afeta outros
- **Segurança** — código de terceiros não acessa o host
- **Paralelismo** — múltiplos testes simultâneos sem conflito

### Por que Redis como fila?

Testes de LLM são operações lentas (1-30 segundos). Usar uma fila assíncrona permite:
- API responde imediatamente sem bloquear
- Worker processa em background
- Frontend consulta status via polling ou WebSocket

### Por que FastAPI?

- Performance superior a Flask para APIs assíncronas
- Documentação automática via OpenAPI/Swagger
- Tipagem nativa com Pydantic
- Suporte nativo a async/await para chamadas de LLM

---

## Database Migrations e Startup

### Alembic (Migration Management)

O SandboxAI utiliza Alembic para versionamento e execução de migrações de banco de dados. Cada mudança no schema é registrada como uma migração SQL reutilizável.

**Migrações existentes:**
- `001_initial.py` — Schema inicial (users, prompts, prompt_versions, test_results)
- `002_add_change_description.py` — Adição do campo `change_description` em `prompt_versions`

**Localização:** `backend/app/migrations/versions/`

### Execução Programática de Migrações

Em vez de usar CLI do Alembic (que causa conflitos de import com ambientes containerizados), o SandboxAI executa migrações programaticamente:

```python
# backend/app/run_migrations.py
async def run_migrations():
    """Executa todas as migrações pendentes ao iniciar a API."""
    config = Config("alembic.ini")
    async with engine.begin() as connection:
        await connection.run_sync(upgrade)
```

Isso garante:
- ✅ Migrations executam automaticamente no startup do container
- ✅ Sem conflitos de CLI em ambientes isolados
- ✅ Sem necessidade de comandos manuais pós-deployment

### Orquestração de Startup

O `entrypoint.sh` coordena a inicialização dos serviços:

```bash
#!/bin/bash

# 1. Aguarda PostgreSQL estar pronto
wait_for_postgres

# 2. Executa migrações (se necessário)
python /app/run_migrations.py

# 3. Inicia API ou Worker conforme variável de ambiente
if [ "$SERVICE_TYPE" = "api" ]; then
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
else
    exec celery -A app.worker worker
fi
```

### Fluxo Completo de Startup

```
docker-compose up
    ↓
container inicia
    ↓
entrypoint.sh executa
    ↓
wait_for_postgres (aguarda conexão)
    ↓
run_migrations.py executa
    ↓
Alembic aplica migrations pendentes
    ↓
API/Worker inicia (pronto para requisições)
```

---

## Celery Worker Architecture

### Fluxo de Processamento de Testes

O Worker é um consumer Celery que processa testes em background:

1. **Enfileiramento** — API coloca tarefa no Redis
   ```python
   execute_test.delay(version_id, test_input)
   ```

2. **Pickup** — Worker consome tarefa da fila
   ```python
   @app.task(bind=True)
   def execute_test(self, version_id, test_input):
       # Process test
   ```

3. **Execução** — Worker chama o provedor configurado
   ```python
   provider = _get_provider(provider_name)
   result = await provider.execute(final_prompt, model, timeout)
   ```

4. **Persistência** — Resultados salvos no PostgreSQL
   ```python
   test_result = TestResult(
       version_id=version_id,
       output=llm_output,
       latency_ms=elapsed_time,
       tokens_used=token_count,
       cost_usd=calculate_cost(tokens_used)
   )
   db.add(test_result)
   ```

### Paralelismo

Múltiplos workers podem rodar em paralelo:

```bash
# Escalar para 4 workers
docker-compose up --scale worker=4
```

Redis garante que cada tarefa seja processada uma única vez, distribuindo entre os workers disponíveis.

---

## Segurança

- Comunicação entre serviços via rede Docker interna (não exposta)
- API Keys de LLMs armazenadas apenas em variáveis de ambiente
- Containers de teste sem acesso à rede do host
- Autenticação JWT em todos os endpoints protegidos

---

## Escalabilidade

Para escalar horizontalmente em produção:

```bash
# Escalar workers para processar mais testes em paralelo
docker compose up --scale worker=4
```

O Redis garante que cada tarefa seja processada por apenas um worker, sem duplicação.
mais testes em paralelo
docker compose up --scale worker=4
```

O Redis garante que cada tarefa seja processada por apenas um worker, sem duplicação.
