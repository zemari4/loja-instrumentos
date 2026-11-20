# CLAUDE.md

Loja Instrumentos (código `musicmais`): e-commerce de instrumentos musicais.
Stack: Django 6 + Python 3.12 + SQLite (Postgres via `DATABASE_URL`) + Redis (cache e rate limit, obrigatório em todos os ambientes: ADR 0002) + templates com Tailwind, HTMX e Alpine.js.

Este arquivo é um **roteador**: aponta para o documento certo por tarefa. Princípio de _progressive disclosure_: **carregue só o que a tarefa exige**; não leia os documentos grandes preventivamente, só quando o gatilho "leia quando" se aplicar.

O projeto segue Spec Driven Development: **a spec é a issue do GitHub** (com PRD em `docs/prd/` quando a mudança é grande). O dono do projeto aprova specs, planos e merges. O método vem do GerenciaLume e está registrado em `docs/adr/0001-adotar-sdd-com-issues-como-spec.md`.

## Roteamento por tarefa

| Sua tarefa | Skill | Leia quando precisar |
|---|---|---|
| Implementar uma issue (feature, bugfix, refactor) | `/implement-pt` | `docs/agent/conventions.md` e `docs/agent/testing.md` (sempre, antes de codar) |
| Escrever ou corrigir testes, ou trabalhar em TDD | `/tdd-pt` | `docs/agent/testing.md` |
| Revisar uma branch ou PR | `/code-review-pt` | `docs/agent/issue-tracker.md` (onde achar a spec) |
| Projetar a interface de um módulo ou decidir onde um seam fica | `/codebase-design-pt` | `docs/agent/conventions.md` |
| Criar issue, branch, commit, PR ou usar labels | — | `docs/agent/issue-tracker.md` e `docs/agent/triage-labels.md` |
| Escrever um PRD de uma mudança grande | — | `docs/prd/_template.md` |
| Registrar uma decisão de arquitetura | — | `docs/adr/README.md` e `docs/adr/_template.md` |
| Entender domínio, vocabulário ou decisões já tomadas | — | `CONTEXT.md` (glossário) e `docs/adr/` (ADRs da área) |
| Entender a estrutura de pastas e apps | — | `docs/agent/structure.md` |
| Mexer em checkout, pedidos ou imagens de produto | — | `docs/orders-checkout.md`, `docs/backstage-imagens-produto.md` |

As skills `*-pt` são globais (`~/.claude/skills`) e leem as regras deste repositório em `docs/agent/`. Para qualquer tarefa de código, comece por `docs/agent/conventions.md`.

## Comandos

```bash
source .venv/bin/activate
pip install -r requirements-dev.txt
docker run -d --name loja-redis -p 127.0.0.1:6379:6379 redis:7-alpine   # Redis, uma vez
python manage.py migrate
python manage.py runserver

ruff check .                              # lint
pytest -q --tb=short                      # suíte completa, saída enxuta
pytest orders/tests/ -k checkout -q       # testes de uma funcionalidade
pytest --cov=. --cov-report=term-missing  # com cobertura (mínimo em pyproject.toml)

cd musicmaisCSS/static_src && npm install && npm run dev    # CSS em watch
```

O que rodar em cada momento, e o gate de conclusão: `docs/agent/testing.md`.

## Fluxo de uma mudança

1. Uma **issue** descreve o que construir e os critérios de aceite (`.github/ISSUE_TEMPLATE/fatia.md`).
2. Branch `<tipo>/<nº-da-issue>-<slug>` (um hook recusa nomes fora do padrão).
3. TDD em seams combinados com o dono, a partir dos critérios de aceite.
4. `/code-review-pt` revisa em dois eixos (padrões e spec).
5. Fragmento de changelog em `changelog.d/<nº-da-issue>.<tipo>.md`.
6. Gate de conclusão verde, PR com `Closes #<nº>`, o dono faz o merge.

Detalhes e formatos: `docs/agent/issue-tracker.md`.

## Exige aprovação explícita do dono

Pare e pergunte antes de:

- Decisões de arquitetura (viram ADR em `docs/adr/`).
- Adicionar, remover ou atualizar dependências.
- Alterar modelos, migrações ou dados existentes.
- Segurança: autenticação, senhas, cifragem (`EncryptedCharField`, `FIELD_ENCRYPTION_KEY`), uploads, permissões do `/manager/`.
- Qualquer integração de pagamento, frete ou nota fiscal.
- Apagar arquivos, reescrever histórico git, mexer em CI e deploy.
- Qualquer ação que publique algo fora da máquina (issue, PR, label, push) quando o dono não a pediu.

## Domínio

- Termos canônicos e termos a evitar: `CONTEXT.md` (não driftar para sinônimos).
- Pagamento é **simulado**: não há gateway real. Pagar.me, Melhor Envio, Focus NFe, Celery, Sentry e S3 aparecem só no `.env.example`, sem código.
- Acesso: cliente vê só os próprios dados; `/manager/` exige `is_staff`.
- Issues: GitHub `zemari4/loja-instrumentos`, via `gh`. Labels: `docs/agent/triage-labels.md`.

## Variáveis de ambiente

Veja `.env.example`. Em dev, `DATABASE_URL` vazio usa SQLite. `FIELD_ENCRYPTION_KEY` é obrigatória em produção.

## Ao terminar uma tarefa

Informe o que mudou, quais comandos rodaram e passaram, e o que ficou sem verificação. Se algo não foi verificado, diga.
