# ⚙️ Variáveis de Ambiente — SandboxAI

Este documento descreve todas as variáveis de ambiente utilizadas pelo projeto.

---

## Como configurar

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite com suas configurações
nano .env
```

---

## Variáveis por serviço

### Docker Compose

| Variável | Obrigatório | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `COMPOSE_PROJECT_NAME` | ❌ | `sandboxai` | Prefixo estável para recursos Docker (containers, network, volumes) |

### API

| Variável | Obrigatório | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `DATABASE_URL` | ✅ | — | URL de conexão com o PostgreSQL |
| `REDIS_URL` | ✅ | — | URL de conexão com o Redis |
| `JWT_SECRET` | ✅ | — | Chave secreta para assinar tokens JWT |
| `JWT_EXPIRE_HOURS` | ❌ | `24` | Tempo de expiração do JWT em horas |
| `DEBUG` | ❌ | `false` | Habilita modo debug |
| `ALLOWED_ORIGINS` | ❌ | `*` | Origens permitidas para CORS |

### Workers

| Variável | Obrigatório | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `REDIS_URL` | ✅ | — | URL de conexão com o Redis |
| `DATABASE_URL` | ✅ | — | URL de conexão com o PostgreSQL |
| `MAX_CONTAINER_TIMEOUT` | ❌ | `60` | Timeout máximo por container em segundos |
| `MAX_CONCURRENT_TESTS` | ❌ | `10` | Número máximo de testes simultâneos |

### Providers de LLM

| Variável | Obrigatório | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `OLLAMA_URL` | ❌ | `http://ollama:11434` | URL do servidor Ollama |
| `GROQ_API_KEY` | ❌ | — | Chave de API do Groq |
| `OPENAI_API_KEY` | ❌ | — | Chave de API da OpenAI |
| `ANTHROPIC_API_KEY` | ❌ | — | Chave de API da Anthropic |

> **Nota:** Ao menos um provider deve ser configurado. Para desenvolvimento, recomendamos usar o Ollama (sem custo) ou o Groq (gratuito com conta).

### PostgreSQL

| Variável | Obrigatório | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `POSTGRES_USER` | ✅ | — | Usuário do banco |
| `POSTGRES_PASSWORD` | ✅ | — | Senha do banco |
| `POSTGRES_DB` | ✅ | — | Nome do banco de dados |

### Frontend

| Variável | Obrigatório | Padrão | Descrição |
|----------|-------------|--------|-----------|
| `VITE_API_URL` | ✅ | — | URL da API backend |

---

## Exemplo de arquivo `.env`

```env
# ─── Docker Compose ───────────────────────────────
COMPOSE_PROJECT_NAME=sandboxai

# ─── API ──────────────────────────────────────────
DATABASE_URL=postgresql://sandboxai:sandboxai@postgres:5432/sandboxai
REDIS_URL=redis://redis:6379
JWT_SECRET=troque-por-uma-chave-secreta-forte
JWT_EXPIRE_HOURS=24
DEBUG=false

# ─── PostgreSQL ───────────────────────────────────
POSTGRES_USER=sandboxai
POSTGRES_PASSWORD=sandboxai
POSTGRES_DB=sandboxai

# ─── Providers de LLM ─────────────────────────────
# Ollama (local, sem custo — recomendado para dev)
OLLAMA_URL=http://ollama:11434

# Groq (gratuito com conta — recomendado para testes)
GROQ_API_KEY=gsk_sua_chave_aqui

# OpenAI (pago — para produção)
# OPENAI_API_KEY=sk-sua_chave_aqui

# Anthropic (pago — para produção)
# ANTHROPIC_API_KEY=sk-ant-sua_chave_aqui

# ─── Frontend ─────────────────────────────────────
VITE_API_URL=http://localhost:8000
```

---

## Obtendo as chaves de API

### Groq (Gratuito)
1. Acesse [console.groq.com](https://console.groq.com)
2. Crie uma conta gratuita
3. Vá em **API Keys** e gere uma nova chave

### Ollama (Sem chave necessária)
O Ollama roda localmente e não exige API Key. Basta ter o container rodando.

### OpenAI
1. Acesse [platform.openai.com](https://platform.openai.com)
2. Vá em **API Keys**
3. Gere uma nova chave secreta

### Anthropic
1. Acesse [console.anthropic.com](https://console.anthropic.com)
2. Vá em **API Keys**
3. Gere uma nova chave

---

## Segurança

> ⚠️ **Nunca commite o arquivo `.env` no repositório.** Ele já está no `.gitignore`.

> ⚠️ **Nunca exponha API Keys em logs, código ou mensagens de commit.**

O arquivo `.env.example` deve sempre estar atualizado com todas as variáveis, mas **sem valores reais**.

---

## Persistência de dados (PostgreSQL)

- Use `docker compose down` para parar o ambiente sem apagar dados.
- Não use `docker compose down -v` em ambiente onde queira preservar dados.
- Evite limpeza ampla (`docker system prune -a -v`) sem backup prévio.
