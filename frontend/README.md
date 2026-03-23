# Frontend SandboxAI — Documentação Completa

> React + TypeScript com tema escuro e integração total com a API REST

## 📁 Estrutura do Projeto

```
frontend/
├── src/
│   ├── components/          # Componentes reutilizáveis
│   │   ├── Header.tsx      # Cabeçalho com navegação
│   │   ├── Alert.tsx       # Notificações (sucesso, erro, aviso)
│   │   ├── Loading.tsx     # Indicador de carregamento
│   │   ├── PromptEditor.tsx # Editor de prompts
│   │   ├── VersionList.tsx  # Lista de versões
│   │   ├── TestRunner.tsx   # Executor de testes
│   │   ├── TestResults.tsx  # Resultados dos testes
│   │   └── PrivateRoute.tsx # Rota protegida por autenticação
│   │
│   ├── pages/               # Páginas da aplicação
│   │   ├── Login.tsx        # Página de login
│   │   ├── Register.tsx     # Página de cadastro
│   │   ├── Dashboard.tsx    # Dashboard com métricas gerais
│   │   ├── PromptList.tsx   # Listagem de prompts
│   │   ├── CreatePrompt.tsx # Criação de novo prompt
│   │   ├── PromptDetail.tsx # Detalhes e edição de prompt
│   │   ├── TestExecution.tsx # Execução de testes
│   │   └── VersionComparison.tsx # Comparação side-by-side
│   │
│   ├── services/            # Serviços de integração
│   │   └── api.ts          # Cliente HTTP (Axios) com autenticação
│   │
│   ├── context/             # Contexto React (estado compartilhado)
│   │   └── AuthContext.tsx  # Autenticação e gerenciamento de usuário
│   │
│   ├── hooks/               # Custom hooks
│   │   └── useApiData.ts    # Hooks para requisições à API
│   │
│   ├── types/               # Tipos TypeScript
│   │   └── index.ts         # Definições de tipos
│   │
│   ├── styles/              # Estilos CSS (tema escuro)
│   │   ├── global.css       # Estilos globais e variáveis CSS
│   │   ├── Header.css
│   │   ├── Auth.css
│   │   ├── Loading.css
│   │   ├── Alert.css
│   │   ├── Dashboard.css
│   │   ├── PromptList.css
│   │   ├── PromptEditor.css
│   │   ├── VersionList.css
│   │   ├── TestRunner.css
│   │   ├── TestResults.css
│   │   ├── PromptDetail.css
│   │   ├── TestExecution.css
│   │   └── VersionComparison.css
│   │
│   ├── App.tsx              # Router principal
│   ├── main.tsx             # Entry point
│   └── index.css            # Estilos padrão (base)
│
├── public/                  # Arquivos estáticos
├── .env.example            # Template de variáveis de ambiente
├── package.json            # Dependências e scripts
├── tsconfig.json          # Configuração TypeScript
├── vite.config.ts         # Configuração Vite
└── README.md              # Este arquivo
```

## 🎨 Tema Escuro

O frontend utiliza **paletra de cores coerente** com tema escuro:

| Cor | Uso |
|-----|-----|
| `#0d1117` | Background primário (página) |
| `#161b22` | Background secundário (cards) |
| `#21262d` | Background terciário (inputs) |
| `#e6edf3` | Texto primário |
| `#c9d1d9` | Texto secundário |
| `#8b949e` | Texto muted |
| `#58a6ff` | Primary (botões, links) |
| `#3fb950` | Success (✅) |
| `#f85149` | Danger (❌) |
| `#d29922` | Warning (⚠️) |

Todas as cores estão definidas em **CSS variables** em `styles/global.css`.

## 🔐 Autenticação

### Fluxo de Login/Registro

```
Login/Register → AuthContext → API Client → localStorage
                   ↓
           (token + user info)
                   ↓
           Protege rotas via PrivateRoute
```

### Endpoints Autenticados

Todos os requests incluem automaticamente o header:
```
Authorization: Bearer <access_token>
```

Token é armazenado em `localStorage` e recuperado ao recarregar a página.

## 📄 Telas Implementadas

### 1. **Login** `/login`
- Email e senha
- Link para cadastro
- Validação básica
- Tratamento de erros

### 2. **Registro** `/register`
- Email, username e senha
- Confirmação de senha
- Link para login
- Mensagens de validação

### 3. **Dashboard** `/dashboard`
- **Métricas Principais:**
  - Total de testes executados
  - Custo total em USD
  - Total de tokens consumidos
  - Latência média
- **Gráficos:**
  - Testes por provider (Ollama, Groq, OpenAI)
  - Testes por status (running, completed, failed, pending)
- Auto-refresh a cada 30 segundos

### 4. **Listagem de Prompts** `/prompts`
- Grid de cards com prompts
- **Busca em tempo real** (debounce de 300ms)
- Filtro por nome
- Actions: Abrir, Testar, Deletar
- Indicador de versão atual (v1, v2, etc)

### 5. **Criação de Prompt** `/create-prompt`
- Formulário com:
  - Nome
  - Descrição
  - Conteúdo do prompt
- Validação
- Dica: `Use {input} para marcar onde a entrada será inserida`

### 6. **Detalhes do Prompt** `/prompts/:id`
- Informações do prompt (nome, descrição, versão)
- **Sidebar com histórico de versões**
  - Clique em versão para comparar
- **TestRunner** para executar testes
- **Comparação side-by-side** de versões

### 7. **Execução de Testes** `/test/:promptId`
- Seleção de:
  - Provider (Ollama, Groq, OpenAI)
  - Modelo específico por provider
- Entrada de teste
- Saída esperada (opcional)
- **Real-time refresh** enquanto executando

### 8. **Resultados de Teste**
- Status badge (pending, running, completed, failed)
- Input/Output/Expected em painéis separados
- **Métricas:**
  - Latência (ms)
  - Tokens de input
  - Tokens de output
  - Custo estimado (USD)
  - Provider e modelo usado

### 9. **Comparação de Versões** `/compare`
- Side-by-side de duas versões
- Visualização de alterações

## 🔌 Integração com API

### Cliente HTTP (Axios)

```typescript
// src/services/api.ts
- Interceptor de request: adiciona token JWT
- Interceptor de response: trata 401 (não autenticado)
- Baseado em tipos TypeScript
```

### Endpoints Consumidos

| Método | Rota | Função |
|--------|------|--------|
| **Auth** | | |
| POST | `/auth/login` | Autenticação |
| POST | `/auth/register` | Cadastro |
| GET | `/auth/profile` | Perfil do usuário |
| **Prompts** | | |
| POST | `/prompts` | Criar prompt |
| GET | `/prompts` | Listar prompts |
| GET | `/prompts/{id}` | Detalhar prompt |
| PUT | `/prompts/{id}` | Editar prompt |
| DELETE | `/prompts/{id}` | Deletar prompt |
| POST | `/prompts/{id}/duplicate` | Duplicar prompt |
| **Versões** | | |
| GET | `/prompts/{id}/versions` | Listar versões |
| GET | `/prompts/{id}/versions/{versionId}` | Detalhes de versão |
| POST | `/prompts/{id}/versions/{versionId}/restore` | Restaurar versão |
| **Testes** | | |
| POST | `/tests` | Executar teste |
| GET | `/tests/{id}` | Status do teste |
| GET | `/tests/{id}/result` | Resultados completos |
| GET | `/prompts/{id}/tests` | Testes de um prompt |
| **Métricas** | | |
| GET | `/metrics` | Métricas globais |
| GET | `/prompts/{id}/metrics` | Métricas por prompt |

## 🎣 Hooks Customizados

### `usePrompts(search?)`
Fetch de lista paginada de prompts com debounce.

### `usePromptDetail(id)`
Fetch de detalhes de um prompt específico.

### `useTestExecution(testId)`
Fetch do status e resultado de um teste executado.

## 🧑‍💻 Desenvolvimento Local

### Pré-requisitos
- Node.js 16+
- npm ou yarn

### Setup

```bash
cd frontend
npm install
cp .env.example .env
# Editar .env conforme necessário
npm run dev
```

Acessa `http://localhost:3000`

### Scripts Disponíveis

```bash
npm run dev          # Modo desenvolvimento com hot reload
npm run build        # Build para produção
npm run preview      # Preview do build
npm run lint         # ESLint
npm run format       # Prettier
npm run test         # Vitest
npm run test:coverage # Coverage report
```

## 📦 Dependências

### Main
- **react** ^18.2.0 — UI library
- **react-dom** ^18.2.0 — DOM binding
- **react-router-dom** ^6.20.0 — Roteamento
- **axios** ^1.6.2 — HTTP client

### Dev
- **TypeScript** ^5.3.3 — Type safety
- **Vite** ^5.0.8 — Build tool
- **Vitest** ^1.0.4 — Test runner
- **ESLint** + **Prettier** — Code quality

## 🌐 Variáveis de Ambiente

### `.env` (Desenvolvimento)

```
# API Backend
VITE_API_URL=http://localhost:8000
```

### CI/CD (GitHub Actions)
Necessários secrets no GitHub:
- `VITE_API_URL` — URL da API em produção

## 🚀 Deploy

### Docker

```dockerfile
FROM node:18 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:18
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist ./dist
EXPOSE 3000
CMD ["serve", "-s", "dist", "-l", "3000"]
```

### Nginx (Reverse Proxy)
Ver `nginx.conf` para produção com gzip, cache headers, etc.

## ✅ Checklist de Requisitos

- ✅ **RF01.1** — Criar prompt
- ✅ **RF01.2** — Editar prompt (nova versão)
- ✅ **RF01.3** — Listar prompts com busca
- ✅ **RF01.4** — Deletar prompt
- ✅ **RF02.1** — Histórico de versões
- ✅ **RF02.2** — Visualizar diff entre versões
- ✅ **RF03.1** — Executar teste com entrada
- ✅ **RF03.4** — Saída esperada para teste
- ✅ **RF04.1** — Registrar latência (ms)
- ✅ **RF04.2** — Registrar tokens
- ✅ **RF04.3** — Calcular custo em USD
- ✅ **RF04.4** — Exibir comparação side-by-side
- ✅ **RF04.5** — Dashboard com métricas agregadas
- ✅ **RF05.5** — Configurar modelo por provider
- ✅ **RF06.1** — Cadastro (email + senha)
- ✅ **RF06.2** — Autenticação JWT
- ✅ **RF06.3** — Isolamento por usuário

## 🐛 Troubleshooting

### "CORS error"
Verificar se `VITE_API_URL` está correto em `.env`

### "Token expirado"
localStorage será limpo automaticamente e usuário redirecionado para `/login`

### "Componente não renderia"
Verificar se está dentro de `<AuthProvider>` (em App.tsx)

## 📝 Notas de Desenvolvimento

1. **Tema escuro** é aplicado globalmente via CSS variables
2. **Tipos TypeScript** garantem segurança de tipos em toda app
3. **Context API** gerencia autenticação (não Redux)
4. **Axios interceptors** tratam autenticação automaticamente
5. **Debounce** em busca reduz chamadas à API
6. **Auto-refresh** em real-time para execução de testes

## 🔗 Links Úteis

- [React Docs](https://react.dev)
- [React Router](https://reactrouter.com)
- [Axios Docs](https://axios-http.com)
- [TypeScript Docs](https://www.typescriptlang.org)
- [Vite Docs](https://vitejs.dev)

---

**Desenvolvido em março de 2026** 🚀
