# 🐇 CodeRabbit Integration Manual (Manual de Integração do CodeRabbit)

Este manual documenta o processo simples de ativação e uso do **CodeRabbit** (assistente de revisão de código baseado em IA) para o repositório do **SandboxAI**.

---

## 🚀 Como Ativar o CodeRabbit no Repositório

A ativação do CodeRabbit é feita de forma visual e rápida através do assistente oficial da plataforma:

1. **Acesse o Assistente de Configuração:**
   Navegue até o assistente visual em:
   👉 **[app.coderabbit.ai/wizard](https://app.coderabbit.ai/wizard)**

2. **Autenticação com o GitHub:**
   - Realize o login utilizando a sua conta do GitHub que possui acesso ao repositório.
   - Caso seja necessário, dê as devidas permissões de leitura/escrita para a organização ou conta pessoal onde o repositório `SandboxAI` está hospedado.

3. **Selecione o Repositório:**
   - No painel do Wizard, localize o repositório `SandboxAI`.
   - Clique no botão **"Add"** ou **"Connect"** ao lado do nome do repositório para iniciar o processo de vinculação.

4. **Configuração Inicial:**
   - Escolha o plano de avaliação ou plano ativo para o repositório.
   - O CodeRabbit aplicará as configurações padrão de revisão automática para Pull Requests.
   - *Nota:* O bot instalará automaticamente o GitHub App na conta/organização correspondente se ainda não estiver instalado.

---

## 🛠️ Como Funciona o Fluxo de Revisão

Uma vez ativado, o CodeRabbit operará automaticamente nos seguintes eventos:

- **Criação de Pull Request (PR):** Sempre que uma nova PR for aberta direcionada para `develop` ou `main`, o CodeRabbit iniciará uma análise automática dos arquivos modificados.
- **Novos Commits:** Sempre que novos commits forem enviados à branch de uma PR aberta, o CodeRabbit atualizará a análise de forma incremental.
- **Comentários de Linha:** O CodeRabbit fará comentários diretamente nas linhas modificadas sugerindo otimizações, correções de bugs, problemas de tipagem ou melhorias gerais.
- **Interação por Chat:** Você pode responder aos comentários do CodeRabbit ou mencionar `@coderabbitai` no chat da PR para pedir refinamentos, explicações adicionais ou geração de código alternativo.

---

## 🛡️ Melhores Práticas para o Squad

1. **Revisão Colaborativa:** Trate o CodeRabbit como um par-programador virtual adicional (junto com o `@architect`, `@backend-lead`, `@frontend-lead` e `@qa-engineer`).
2. **Resolução de Comentários:** Antes de mesclar a PR, revise todas as sugestões do CodeRabbit. Se a sugestão fizer sentido, aplique-a. Se for um falso positivo, você pode simplesmente marcar como resolvido ou ignorar com uma breve justificativa.
3. **Mantenha as Regras Hardened:** Lembre-se que, além da revisão por IA do CodeRabbit, todas as diretrizes do `AGENTS.md` continuam ativas e devem ser plenamente cumpridas antes do merge.
