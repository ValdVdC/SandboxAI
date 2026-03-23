# 🚀 SandboxAI

> Plataforma de versionamento, teste e comparação de prompts para LLMs — tratando prompt engineering com o rigor de engenharia de software.

![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)
![Docker](https://img.shields.io/badge/docker-ready-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Funcionalidades](#funcionalidades)
- [Arquitetura](#arquitetura)
- [Tecnologias](#tecnologias)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Como Usar](#como-usar)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Documentação](#documentação)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## 📖 Sobre o Projeto

O **SandboxAI** nasceu de um problema real: times que desenvolvem aplicações com IA não têm onde versionar, comparar e testar prompts de forma sistemática. Cada desenvolvedor testa no próprio chat de forma desorganizada, sem histórico, sem métricas e sem colaboração.

O SandboxAI resolve isso tratando prompts como código — com versionamento, testes automatizados, ambientes isolados e métricas de qualidade.

### O problema que resolvemos

```
Sem SandboxAI                          Com SandboxAI
─────────────────────────────────────────────────────
❌ Prompts espalhados em chats         ✅ Prompts versionados como código
❌ Sem histórico de mudanças           ✅ Histórico completo de versões
❌ Resultados inconsistentes           ✅ Ambientes Docker isolados
❌ Sem métricas de custo               ✅ Métricas de custo e latência
❌ Sem colaboração em time             ✅ Compartilhamento e revisão
```

---

## ✨ Funcionalidades

- **Versionamento de Prompts** — histórico completo de todas as versões, como Git para prompts
- **Ambientes Isolados** — cada teste roda em um container Docker dedicado, garantindo reprodutibilidade
- **Comparação Side-by-Side** — compare resultados de diferentes versões de um mesmo prompt
- **Métricas Detalhadas** — custo estimado, latência, tokens consumidos por teste
- **Multi-Provider** — suporte a OpenAI, Anthropic, Groq e Ollama (local)
- **Testes Automatizados** — defina critérios de qualidade e rode baterias de testes automaticamente
- **Colaboração em Time** — compartilhe prompts, comente versões e trabalhe em conjunto

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────┐
│                    SandboxAI                        │
│                                                     │
│  ┌──────────┐    ┌──────────┐    ┌──────────────┐  │
│  │ Frontend │───▶│   API    │───▶│    Worker    │  │
│  │ (React)  │    │(FastAPI) │    │  (Executor)  │  │
│  └──────────┘    └──────────┘    └──────┬───────┘  │
│                       │                 │           │
│                  ┌────┴────┐    ┌───────▼───────┐  │
│                  │  Redis  │    │ Container Pool│  │
│                  │ (Fila)  │    │  (por teste)  │  │
│                  └─────────┘    └───────────────┘  │
│                       │                            │
│                  ┌────┴────┐                       │
│                  │Postgres │                       │
│                  │  (DB)   │                       │
│                  └─────────┘                       │
└─────────────────────────────────────────────────────┘
```

Para mais detalhes, veja [ARCHITECTURE.md](./ARCHITECTURE.md).

---

## 🛠️ Tecnologias

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11 + FastAPI |
| Frontend | React + TypeScript |
| Banco de Dados | PostgreSQL 15 |
| Fila | Redis 7 |
| Containerização | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| LLM Local | Ollama |
| Testes | Pytest + Vitest |

---

## ✅ Pré-requisitos

- [Docker](https://docs.docker.com/get-docker/) >= 24.0
- [Docker Compose](https://docs.docker.com/compose/) >= 2.0
- [Git](https://git-scm.com/)

> **Nota:** Não é necessário instalar Python ou Node.js localmente — tudo roda dentro dos containers.

---

## 🚀 Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/sandboxai.git
cd sandboxai
```

### 2. Configure as variáveis de ambiente

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas chaves de API (veja [ENVIRONMENT.md](./ENVIRONMENT.md)).

### 3. Suba os containers

```bash
docker compose up -d
```

### 4. Acesse a aplicação

```
http://localhost:3000
```

---

## 💻 Como Usar

### Criando seu primeiro prompt

```bash
# Via API
curl -X POST http://localhost:8000/prompts \
  -H "Content-Type: application/json" \
  -d '{
    "name": "classificador-sentimento",
    "content": "Classifique o sentimento do texto a seguir como positivo, negativo ou neutro: {input}",
    "provider": "groq",
    "model": "llama-3.3-70b-versatile"
  }'
```

### Rodando um teste

```bash
curl -X POST http://localhost:8000/prompts/{id}/test \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Adorei o produto, superou minhas expectativas!",
    "expected": "positivo"
  }'
```

---

## 📁 Estrutura do Projeto

```
sandboxai/
├── .github/
│   └── workflows/          # Pipelines GitHub Actions
│       ├── ci.yml
│       ├── release.yml
│       └── security.yml
├── backend/
│   ├── app/
│   │   ├── api/            # Endpoints REST
│   │   ├── core/           # Configurações e utilitários
│   │   ├── models/         # Modelos do banco de dados
│   │   ├── services/       # Lógica de negócio
│   │   └── workers/        # Executores de testes
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── Dockerfile
│   └── package.json
├── docker/
│   └── ollama/             # Configuração do Ollama local
├── docs/                   # Documentação completa
├── .env.example
├── docker-compose.yml
└── README.md
```

---

## 📚 Documentação

| Documento | Descrição |
|-----------|-----------|
| [ARCHITECTURE.md](./ARCHITECTURE.md) | Arquitetura técnica detalhada |
| [REQUIREMENTS.md](./REQUIREMENTS.md) | Requisitos funcionais e não funcionais |
| [CONTRIBUTING.md](./CONTRIBUTING.md) | Guia de contribuição |
| [CHANGELOG.md](./CHANGELOG.md) | Histórico de versões |
| [SECURITY.md](./SECURITY.md) | Política de segurança |
| [ENVIRONMENT.md](./ENVIRONMENT.md) | Variáveis de ambiente |

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Veja [CONTRIBUTING.md](./CONTRIBUTING.md) para saber como começar.

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](./LICENSE) para mais detalhes.

---

<p align="center">Desenvolvido como projeto acadêmico para a cadeira de Tópicos Integradores</p>
