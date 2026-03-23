# 🔒 Política de Segurança — SandboxAI

## Reportando uma Vulnerabilidade

Se você descobriu uma vulnerabilidade de segurança no SandboxAI, **não abra uma Issue pública**. Isso poderia expor outros usuários antes que o problema seja corrigido.

Em vez disso, envie um email diretamente para o time com:

- Descrição detalhada da vulnerabilidade
- Passos para reproduzir
- Impacto potencial
- Sugestão de correção (se houver)

Você receberá uma resposta em até 48 horas.

---

## Práticas de Segurança do Projeto

### Credenciais e Segredos
- API Keys e senhas são armazenadas **apenas em variáveis de ambiente**
- O arquivo `.env` está no `.gitignore` e nunca é commitado
- O arquivo `.env.example` contém apenas chaves, sem valores reais

### Containers Docker
- Containers de execução de testes **não têm acesso à rede do host**
- Cada container de teste é destruído imediatamente após a execução
- Containers rodam com usuário não-root sempre que possível

### Comunicação entre Serviços
- Serviços se comunicam pela **rede interna Docker**, não exposta externamente
- Apenas as portas necessárias são expostas ao host

### Autenticação
- Senhas armazenadas com **hash bcrypt**
- Autenticação via **JWT** com expiração configurável
- Tokens expiram em no máximo 24 horas por padrão

### CI/CD
- Scan automático de vulnerabilidades em todas as imagens Docker via **Trivy**
- Pull Requests bloqueados se vulnerabilidades críticas forem encontradas

---

## Versões Suportadas

| Versão | Suportada |
|--------|-----------|
| Latest | ✅ |
| Anteriores | ❌ |

Recomendamos sempre usar a versão mais recente.
