# 🗺️ Roadmap — SandboxAI

Este documento descreve o planejamento de desenvolvimento do SandboxAI, organizado em fases.

---

## Fase 1 — MVP Acadêmico (Concluída)

Objetivo: entregar uma versão funcional para o seminário de Tópicos Integradores.

- [x] Documentação completa do projeto
- [x] Estrutura base do Docker Compose
- [x] API com endpoints de CRUD de prompts
- [x] Versionamento básico de prompts
- [x] Integração com Ollama (local)
- [x] Integração com Groq
- [x] Registro de métricas básicas (latência, tokens, custo)
- [x] Frontend funcional para criar e testar prompts
- [x] Autenticação completa com JWT (User login/register)
- [x] Integração com OpenAI e Anthropic (Backend)
- [x] Dashboard básico de métricas e custos

---

## Fase 2 — Produto (Em andamento)

Objetivo: evoluir para um produto utilizável por outros desenvolvedores.

- [ ] Comparação side-by-side de versões (Visual Diff)
- [ ] Baterias de testes automatizados (Bulk Testing)
- [ ] Exportação de resultados em CSV
- [ ] Documentação da API pública (Swagger/Redoc)
- [ ] Sandbox Real (Docker-in-Docker para isolamento total)
- [ ] Pipeline CI/CD completo com GitHub Actions

---

## Fase 3 — SaaS

Objetivo: transformar em um serviço escalável e monetizável.

- [ ] Sistema de planos (Free, Pro, Teams)
- [ ] Compartilhamento de prompts entre usuários
- [ ] Webhooks para notificações externas
- [ ] Integração com GitHub (importar prompts de repositórios)
- [ ] Suporte a modelos customizados via fine-tuning

---

## 🛠️ Dívida Técnica & Próximos Passos Imediatos

1. **Refatoração de Datas:** Migrar de `utcnow()` para `now(timezone.utc)` (Concluído ✅)
2. **Segurança JWT:** Remover segredos padrão do código (Concluído ✅)
3. **Isolamento:** Implementar o runner em Docker conforme planejado originalmente na arquitetura.
4. **UX:** Implementar o componente de comparação visual na página de `VersionComparison`.
