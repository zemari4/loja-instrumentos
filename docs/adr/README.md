# Decisões de arquitetura (ADRs)

Um ADR (Architecture Decision Record) registra **uma** decisão importante: o contexto, a decisão e as consequências. Quem decide é o dono do projeto. A IA pode levantar opções e rascunhar, mas um ADR só vira `accepted` com a aprovação dele.

## Como usar

1. Copie `_template.md` para `NNNN-titulo-curto-em-portugues.md`. Numeração sequencial, sem reaproveitar números (confira o último antes de criar, para não repetir).
2. Preencha contexto e opções. Deixe o status como `proposed`.
3. O dono muda o status para `accepted (issue #N, data)` ou `rejected`.
4. Uma decisão que muda não é editada: crie outro ADR e marque o antigo como `superseded by NNNN`.

Um ADR nasce de uma issue (`docs/agent/issue-tracker.md`) ou é citado por uma. Specs e PRDs apontam para os ADRs que respeitam.

## Índice

| Nº | Decisão | Status |
|---|---|---|
| [0001](0001-adotar-sdd-com-issues-como-spec.md) | Adotar SDD com a issue como spec | accepted |

## Decisões em aberto

Levantadas no panorama tecnológico. Cada uma vira um ADR (e uma issue com a label `question`) quando for a hora de decidir.

| Tema | Pergunta | Evidência hoje |
|---|---|---|
| Banco de dados | SQLite ou PostgreSQL em produção? | `.env.example` aponta para Postgres, mas `psycopg` não está nos requirements |
| Tailwind | CSS compilado ou Play CDN nas páginas públicas? | ~12 templates carregam `cdn.tailwindcss.com` ao lado do CSS compilado |
| Mídia | Disco local ou armazenamento S3/MinIO? | variáveis S3 no `.env.example`, sem `django-storages` |
| Cache e filas | Redis e Celery serão adotados? | só variáveis no `.env.example`, `backend/celery.py` está vazio |
| Observabilidade | Sentry ou outra ferramenta? | só variáveis no `.env.example` |
| Pagamento | Qual gateway (Pagar.me ou outro)? | pagamento simulado, modelo `Payment` pronto |
| Frete | Qual serviço de cálculo e etiqueta? | sem implementação |
| Nota fiscal | Qual serviço de emissão? | sem implementação |
| Deploy | Onde e como será publicado? | há menção a PythonAnywhere no changelog, sem config no repositório |
| Testes de ponta a ponta | Adotar Playwright? | marker `e2e` no `pyproject.toml`, ferramenta não instalada |
