# 📋 Requisitos — SandboxAI

## Requisitos Funcionais

Requisitos funcionais descrevem **o que o sistema deve fazer** — as funcionalidades e comportamentos esperados.

---

### RF01 — Gerenciamento de Prompts

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF01.1 | O sistema deve permitir criar um prompt com nome, descrição e conteúdo | Alta |
| RF01.2 | O sistema deve permitir editar um prompt existente, gerando uma nova versão automaticamente | Alta |
| RF01.3 | O sistema deve listar todos os prompts do usuário com filtros por nome e data | Alta |
| RF01.4 | O sistema deve permitir excluir um prompt e todas as suas versões | Média |
| RF01.5 | O sistema deve permitir duplicar um prompt como ponto de partida para um novo | Baixa |

---

### RF02 — Versionamento

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF02.1 | O sistema deve manter histórico completo de todas as versões de cada prompt | Alta |
| RF02.2 | O sistema deve permitir visualizar o diff entre duas versões de um prompt | Alta |
| RF02.3 | O sistema deve permitir restaurar uma versão anterior de um prompt | Média |
| RF02.4 | O sistema deve associar uma mensagem descritiva a cada nova versão | Baixa |

---

### RF03 — Execução de Testes

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF03.1 | O sistema deve permitir executar um teste com uma entrada específica para qualquer versão de prompt | Alta |
| RF03.2 | Cada teste deve rodar em um container Docker isolado | Alta |
| RF03.3 | O sistema deve suportar ao menos os providers: Ollama, Groq e OpenAI | Alta |
| RF03.4 | O sistema deve permitir definir uma saída esperada para o teste | Média |
| RF03.5 | O sistema deve permitir executar baterias de testes com múltiplas entradas simultaneamente | Média |
| RF03.6 | O sistema deve notificar o usuário ao concluir um teste assíncrono | Baixa |

---

### RF04 — Métricas e Resultados

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF04.1 | O sistema deve registrar a latência (ms) de cada teste | Alta |
| RF04.2 | O sistema deve registrar a quantidade de tokens consumidos por teste | Alta |
| RF04.3 | O sistema deve calcular e exibir o custo estimado em USD por teste | Alta |
| RF04.4 | O sistema deve exibir os resultados em uma interface de comparação side-by-side | Alta |
| RF04.5 | O sistema deve exibir um dashboard com métricas agregadas de uso | Média |
| RF04.6 | O sistema deve permitir exportar resultados em formato CSV | Baixa |

---

### RF05 — Providers de LLM

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF05.1 | O sistema deve suportar o provider Ollama para execução local e gratuita | Alta |
| RF05.2 | O sistema deve suportar o provider Groq | Alta |
| RF05.3 | O sistema deve suportar o provider OpenAI | Média |
| RF05.4 | O sistema deve suportar o provider Anthropic | Média |
| RF05.5 | O sistema deve permitir configurar o modelo específico por provider | Alta |
| RF05.6 | O sistema deve validar a disponibilidade do provider antes de executar um teste | Média |

---

### RF06 — Autenticação e Usuários

| ID | Requisito | Prioridade |
|----|-----------|-----------|
| RF06.1 | O sistema deve permitir cadastro de usuários via email e senha | Alta |
| RF06.2 | O sistema deve autenticar usuários via JWT | Alta |
| RF06.3 | O sistema deve garantir que cada usuário acesse apenas seus próprios prompts | Alta |
| RF06.4 | O sistema deve permitir compartilhar um prompt com outro usuário via link | Baixa |

---

## Requisitos Não Funcionais

Requisitos não funcionais descrevem **como o sistema deve se comportar** — qualidade, desempenho e restrições técnicas.

---

### RNF01 — Desempenho

| ID | Requisito |
|----|-----------|
| RNF01.1 | A API deve responder requisições de leitura em no máximo 500ms |
| RNF01.2 | O enfileiramento de um teste deve ocorrer em no máximo 200ms |
| RNF01.3 | O sistema deve suportar ao menos 10 testes simultâneos sem degradação |
| RNF01.4 | O frontend deve carregar em no máximo 3 segundos em conexão padrão |

---

### RNF02 — Disponibilidade

| ID | Requisito |
|----|-----------|
| RNF02.1 | O sistema deve ter disponibilidade mínima de 99% em ambiente de produção |
| RNF02.2 | Falha em um container de teste não deve derrubar os demais serviços |
| RNF02.3 | O sistema deve realizar health checks automáticos em todos os containers |

---

### RNF03 — Segurança

| ID | Requisito |
|----|-----------|
| RNF03.1 | API Keys de providers de LLM devem ser armazenadas apenas em variáveis de ambiente, nunca no código |
| RNF03.2 | Containers de execução de testes não devem ter acesso à rede do host |
| RNF03.3 | Toda comunicação entre serviços deve ocorrer pela rede interna Docker |
| RNF03.4 | Senhas de usuários devem ser armazenadas com hash bcrypt |
| RNF03.5 | Tokens JWT devem expirar em no máximo 24 horas |
| RNF03.6 | O pipeline de CI/CD deve executar scan de vulnerabilidades em todas as imagens Docker |

---

### RNF04 — Manutenibilidade

| ID | Requisito |
|----|-----------|
| RNF04.1 | O código deve ter cobertura mínima de 70% por testes automatizados |
| RNF04.2 | Cada serviço deve ter seu próprio Dockerfile com build multi-stage |
| RNF04.3 | Variáveis de ambiente devem ser documentadas no arquivo `.env.example` |
| RNF04.4 | A API deve expor documentação automática via Swagger/OpenAPI |

---

### RNF05 — Portabilidade

| ID | Requisito |
|----|-----------|
| RNF05.1 | O sistema deve funcionar em qualquer ambiente com Docker instalado |
| RNF05.2 | O comando `docker compose up` deve ser suficiente para subir o ambiente completo |
| RNF05.3 | O sistema deve funcionar nos sistemas operacionais Linux, macOS e Windows |

---

### RNF06 — Observabilidade

| ID | Requisito |
|----|-----------|
| RNF06.1 | Todos os serviços devem gerar logs estruturados em formato JSON |
| RNF06.2 | O sistema deve expor um endpoint `/health` em cada serviço |
| RNF06.3 | Erros críticos devem ser registrados com stack trace completo |

---

## Regras de Negócio

| ID | Regra |
|----|-------|
| RN01 | Uma nova versão de prompt é criada automaticamente a cada edição — não é possível sobrescrever uma versão existente |
| RN02 | Um teste só pode ser executado se o provider configurado estiver disponível |
| RN03 | Containers de teste são destruídos automaticamente ao final da execução, independente do resultado |
| RN04 | O custo estimado é calculado com base na tabela de preços de cada provider no momento do teste |
| RN05 | Resultados de testes são imutáveis após gerados — não podem ser editados |

---

## Casos de Uso Principais

### UC01 — Criar e testar um prompt

```
Ator: Desenvolvedor

Pré-condição: Usuário autenticado

Fluxo principal:
1. Usuário acessa a tela de novo prompt
2. Preenche nome, descrição e conteúdo do prompt
3. Seleciona provider e modelo
4. Salva o prompt (versão 1 criada automaticamente)
5. Insere uma entrada de teste
6. Clica em "Executar Teste"
7. Sistema enfileira o teste no Redis
8. Worker cria container isolado e executa o prompt
9. Resultado é exibido com latência, tokens e custo

Pós-condição: Resultado salvo no banco vinculado à versão 1
```

### UC02 — Comparar versões de um prompt

```
Ator: Desenvolvedor

Pré-condição: Prompt com ao menos 2 versões e testes executados

Fluxo principal:
1. Usuário acessa o histórico de versões do prompt
2. Seleciona duas versões para comparar
3. Sistema exibe diff do conteúdo dos prompts
4. Sistema exibe resultados side-by-side com métricas
5. Usuário identifica qual versão tem melhor performance

Pós-condição: Nenhuma alteração de estado
```
