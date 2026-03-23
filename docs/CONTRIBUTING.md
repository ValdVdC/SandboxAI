# 🤝 Guia de Contribuição — SandboxAI

Obrigado pelo interesse em contribuir com o SandboxAI! Este guia explica como configurar o ambiente, seguir os padrões do projeto e submeter suas contribuições.

---

## 📋 Índice

- [Código de Conduta](#código-de-conduta)
- [Como Contribuir](#como-contribuir)
- [Configurando o Ambiente](#configurando-o-ambiente)
- [Padrões de Código](#padrões-de-código)
- [Commits](#commits)
- [Pull Requests](#pull-requests)
- [Reportando Bugs](#reportando-bugs)
- [Sugerindo Melhorias](#sugerindo-melhorias)

---

## 📜 Código de Conduta

Este projeto adota um ambiente colaborativo e respeitoso. Esperamos que todos os contribuidores:

- Usem linguagem inclusiva e respeitosa
- Aceitem críticas construtivas com abertura
- Foquem no que é melhor para o projeto
- Demonstrem empatia com outros contribuidores

---

## 🚀 Como Contribuir

### 1. Faça um fork do repositório

```bash
# Fork via GitHub e então clone
git clone https://github.com/seu-usuario/sandboxai.git
cd sandboxai
```

### 2. Crie uma branch para sua contribuição

```bash
# Sempre parta da branch main atualizada
git checkout main
git pull origin main

# Crie sua branch seguindo o padrão
git checkout -b feat/nome-da-feature
# ou
git checkout -b fix/nome-do-bug
```

### 3. Faça suas alterações

Siga os [padrões de código](#padrões-de-código) descritos abaixo.

### 4. Rode os testes

```bash
# Backend
docker compose run --rm api pytest

# Frontend
docker compose run --rm frontend npm test
```

### 5. Abra um Pull Request

Siga o template de [Pull Request](#pull-requests).

---

## ⚙️ Configurando o Ambiente

### Pré-requisitos

- Docker >= 24.0
- Docker Compose >= 2.0
- Git

### Setup inicial

```bash
# 1. Clone o repositório
git clone https://github.com/seu-usuario/sandboxai.git
cd sandboxai

# 2. Copie o arquivo de variáveis de ambiente
cp .env.example .env

# 3. Suba os containers em modo desenvolvimento
docker compose -f docker-compose.dev.yml up -d

# 4. Verifique se todos os serviços estão saudáveis
docker compose ps
```

### Verificando o ambiente

```bash
# API deve responder
curl http://localhost:8000/health

# Frontend deve estar acessível
open http://localhost:3000

# Logs de todos os serviços
docker compose logs -f
```

---

## 📐 Padrões de Código

### Python (Backend)

O projeto usa **Black** para formatação e **Ruff** para linting.

```bash
# Formatar código
docker compose run --rm api black .

# Verificar linting
docker compose run --rm api ruff check .
```

**Convenções:**
- Funções e variáveis em `snake_case`
- Classes em `PascalCase`
- Constantes em `UPPER_SNAKE_CASE`
- Docstrings em todas as funções públicas
- Type hints obrigatórios em funções da API

```python
# ✅ Correto
async def execute_test(prompt_id: UUID, input_data: str) -> TestResult:
    """
    Executa um teste para a versão mais recente do prompt.

    Args:
        prompt_id: ID do prompt a ser testado
        input_data: Texto de entrada para o teste

    Returns:
        Resultado do teste com métricas
    """
    ...

# ❌ Evitar
async def executeTest(promptId, input):
    ...
```

### TypeScript (Frontend)

O projeto usa **ESLint** e **Prettier** para formatação.

```bash
# Formatar código
docker compose run --rm frontend npm run format

# Verificar linting
docker compose run --rm frontend npm run lint
```

**Convenções:**
- Componentes React em `PascalCase`
- Funções e variáveis em `camelCase`
- Arquivos de componentes em `PascalCase.tsx`
- Hooks customizados com prefixo `use`

```typescript
// ✅ Correto
const PromptCard = ({ prompt }: PromptCardProps) => {
  const { executeTest } = usePromptTest(prompt.id);
  ...
}

// ❌ Evitar
const prompt_card = ({ prompt }) => {
  ...
}
```

### Testes

- **Backend:** Pytest com cobertura mínima de 70%
- **Frontend:** Vitest + React Testing Library

```bash
# Rodar testes com cobertura
docker compose run --rm api pytest --cov=app --cov-report=term-missing

# Rodar testes do frontend
docker compose run --rm frontend npm run test:coverage
```

---

## 💬 Commits

O projeto segue o padrão [Conventional Commits](https://www.conventionalcommits.org/).

### Formato

```
<tipo>(<escopo>): <descrição curta>

[corpo opcional]

[rodapé opcional]
```

### Tipos permitidos

| Tipo | Quando usar |
|------|-------------|
| `feat` | Nova funcionalidade |
| `fix` | Correção de bug |
| `docs` | Alterações na documentação |
| `style` | Formatação, sem alteração de lógica |
| `refactor` | Refatoração sem nova feature ou bug fix |
| `test` | Adição ou correção de testes |
| `chore` | Tarefas de manutenção, CI/CD |
| `perf` | Melhoria de performance |

### Exemplos

```bash
# ✅ Correto
git commit -m "feat(prompts): adicionar suporte ao provider Anthropic"
git commit -m "fix(worker): corrigir timeout em containers de teste"
git commit -m "docs(readme): atualizar instruções de instalação"
git commit -m "test(api): adicionar testes para endpoint de métricas"

# ❌ Evitar
git commit -m "fix bug"
git commit -m "changes"
git commit -m "WIP"
```

---

## 🔀 Pull Requests

### Antes de abrir um PR

- [ ] Testes passando localmente
- [ ] Cobertura de testes mantida ou aumentada
- [ ] Código formatado e lint sem erros
- [ ] Documentação atualizada se necessário
- [ ] Branch atualizada com a `main`

### Template de PR

Ao abrir um PR, preencha o template:

```markdown
## Descrição
Breve descrição do que foi implementado ou corrigido.

## Tipo de mudança
- [ ] Nova feature
- [ ] Bug fix
- [ ] Refatoração
- [ ] Documentação

## Como testar
1. Passo 1
2. Passo 2
3. Resultado esperado

## Checklist
- [ ] Testes adicionados/atualizados
- [ ] Documentação atualizada
- [ ] Sem warnings de linting
```

### Processo de revisão

1. Abra o PR contra a branch `main`
2. O GitHub Actions rodará os testes automaticamente
3. Pelo menos uma aprovação é necessária para merge
4. Após aprovação, o merge será feito via **Squash and Merge**

---

## 🐛 Reportando Bugs

Use o template de Issue para bugs:

```markdown
**Descrição do bug**
Descrição clara e concisa do problema.

**Como reproduzir**
1. Acesse '...'
2. Clique em '...'
3. Veja o erro

**Comportamento esperado**
O que deveria acontecer.

**Screenshots**
Se aplicável.

**Ambiente**
- OS: [ex: Ubuntu 22.04]
- Docker: [ex: 24.0.5]
- Browser: [ex: Chrome 120]
```

---

## 💡 Sugerindo Melhorias

Para sugerir uma nova feature, abra uma Issue com o label `enhancement` descrevendo:

- **Problema** que a feature resolve
- **Solução proposta**
- **Alternativas consideradas**
- **Contexto adicional**

---

## 📁 Estrutura de Branches

| Branch | Propósito |
|--------|-----------|
| `main` | Código estável, pronto para produção |
| `feat/*` | Novas funcionalidades |
| `fix/*` | Correção de bugs |
| `docs/*` | Atualizações de documentação |
| `chore/*` | Tarefas de manutenção |

---

Dúvidas? Abra uma Issue com o label `question`. 🙋
