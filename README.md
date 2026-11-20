# Loja Instrumentos

**Loja Instrumentos** é uma loja virtual completa de instrumentos musicais. O projeto cobre tudo que uma loja online precisa: vitrine de produtos, carrinho de compras, checkout, gestão de pedidos e painel administrativo — tudo em um único sistema web.

---

## O que é este projeto?

É um e-commerce (loja virtual) focado em instrumentos musicais. Clientes podem:

- Navegar pelo catálogo de produtos
- Adicionar itens ao carrinho
- Finalizar compras com checkout integrado
- Acompanhar o histórico de pedidos
- Criar e gerenciar sua conta

Administradores têm acesso a um painel para gerenciar produtos, estoque, pedidos e visualizar métricas da loja.

---

## Tecnologias utilizadas

### Backend (servidor)

| Tecnologia | O que faz |
|---|---|
| **Python** | Linguagem de programação principal do projeto |
| **Django** | Framework web que cuida das rotas, banco de dados, autenticação e toda a lógica do servidor |
| **SQLite** | Banco de dados padrão do projeto local (basta um arquivo, sem servidor para instalar) |
| **django-allauth** | Cadastro e login (inclui login com Google, que depende de credenciais configuradas no admin) |
| **django-jazzmin** | Tema do painel `/admin/` |
| **django-crispy-forms** | Renderização de formulários com o pack Tailwind |
| **django-simple-history** | Histórico de alterações dos modelos |
| **django-import-export** | Importação e exportação de produtos |
| **django-ratelimit** | Limite de requisições em rotas sensíveis |
| **cryptography (Fernet)** | Cifragem de campos sensíveis, como o CPF do perfil |
| **Pillow** | Upload e processamento de imagens de produto e carrossel |
| **WhiteNoise** | Entrega dos arquivos estáticos em produção |

### Frontend (interface visual)

| Tecnologia | O que faz |
|---|---|
| **TailwindCSS v4** | Sistema de estilização. O CSS é compilado em `musicmaisCSS/static_src`. Vários templates ainda carregam também o Tailwind Play CDN (decisão em aberto, veja `docs/adr/`) |
| **DaisyUI 5** | Componentes visuais prontos (botões, cards, badges), habilitado como plugin do Tailwind |
| **HTMX** | Permite atualizar partes da página sem recarregar tudo. Carregado por CDN no layout do manager |
| **Alpine.js** | Pequenas interações diretamente nos elementos HTML (ex: abrir/fechar menus). Carregado por CDN |
| **Font Awesome 6** | Ícones, carregados por CDN no layout do manager |

### Qualidade e processo

| Ferramenta | O que faz |
|---|---|
| **pytest** | Roda os testes automatizados para garantir que o sistema funciona corretamente |
| **Ruff** | Lint de código (configurado em `pyproject.toml`; ainda não roda no CI) |
| **towncrier** | Gera o changelog a partir dos fragmentos em `changelog.d/<nº-da-issue>.<tipo>.md` (vem no `requirements-dev.txt`) |
| **GitHub Actions** | CI: roda `pytest` a cada push e pull request para `main` |
| **Docker** | `Dockerfile.dev` e `docker-compose.yml` para ambiente de desenvolvimento |

### Ainda não implementado

Aparecem no `.env.example`, mas **não têm código** no projeto hoje:

- **Pagamento:** o pagamento é simulado. A integração com Pagar.me (ou outro gateway) é uma etapa futura.
- **Frete** (Melhor Envio) e **nota fiscal** (Focus NFe).
- **Redis, Celery, Sentry e armazenamento S3/MinIO:** o cache é em memória, os arquivos de mídia vão para o disco e não há filas nem monitoramento de erros.
- **PostgreSQL:** o projeto aceita `DATABASE_URL`, mas o driver `psycopg` não está nos requirements.

---

## Estrutura do projeto

```
loja-instrumentos/
├── backend/            # Configuração do Django (settings, urls, wsgi)
├── home/               # Página inicial e carrossel
├── authentication/     # Login, cadastro e conta do usuário
├── catalog/            # Catálogo de produtos
├── cart/               # Carrinho de compras
├── orders/             # Pedidos e histórico de compras
├── manager/            # Painel administrativo da loja (rota /manager/)
├── dashboard/          # Serviços de métricas, estoque e pedidos do painel
├── analytics/          # Middleware de contexto de log e métricas
├── musicmaisCSS/       # App do Tailwind (fonte em static_src, CSS compilado)
├── theme/              # App de tema (scaffolding do django-tailwind)
├── templates/          # Templates HTML de todas as páginas
├── static/             # Imagens e assets estáticos
├── changelog.d/        # Fragmentos de changelog (towncrier)
├── docs/               # Regras de trabalho, ADRs, PRDs e documentação técnica
│   ├── agent/          # Regras para agentes: issues, testes, convenções, estrutura
│   ├── adr/            # Decisões de arquitetura
│   └── prd/            # PRDs de mudanças grandes
├── CONTEXT.md          # Vocabulário do domínio
└── CLAUDE.md           # Roteador de regras de trabalho para agentes de IA
```

---

## Como rodar localmente

### Pré-requisitos

- Python 3.12+ (exigido pelo `pyproject.toml` e pelo Django 6)
- Node.js — apenas se for recompilar o CSS; o projeto já vem com o CSS buildado

### Passos

```bash
# 1. Clone o repositório
git clone git@github.com:zemari4/loja-instrumentos.git
cd loja-instrumentos

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 3. Instale as dependências Python
# Use o requirements-dev.txt: o settings_dev importa debug_toolbar
# e django_browser_reload, que não estão no requirements.txt.
pip install -r requirements-dev.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Deixe DATABASE_URL vazio para usar SQLite. O valor de exemplo aponta
# para um Postgres que não existe localmente e impede o servidor de subir.

# 5. Rode as migrações do banco de dados
python manage.py migrate

# 6. Crie um usuário administrador (para acessar /admin/)
python manage.py createsuperuser

# 7. Inicie o servidor
python manage.py runserver
```

Em outro terminal, para compilar o CSS automaticamente:

```bash
cd musicmaisCSS/static_src && npm install && npm run dev
```

---

## Rodando os testes

```bash
pytest                                        # todos os testes
pytest <app>/tests/ -x                        # testes de um app específico
pytest --cov=. --cov-report=term-missing      # com relatório de cobertura
```

---

## Como evoluir o projeto (Spec Driven Development)

Mudanças de comportamento começam por uma **issue** aprovada pelo dono do projeto, não pelo código. A issue é a spec: descreve o que construir e os critérios de aceite, e cada critério vira um teste.

1. Abra a issue a partir do template (`.github/ISSUE_TEMPLATE/fatia.md`). Mudança grande ganha antes um PRD em `docs/prd/`.
2. Crie a branch `<tipo>/<nº-da-issue>-<slug>` e implemente com TDD.
3. Abra o PR com `Closes #<nº>` e um fragmento em `changelog.d/<nº>.<tipo>.md`.
4. Decisões de arquitetura ficam em `docs/adr/`. O vocabulário do domínio está em `CONTEXT.md`.

As regras completas, inclusive o que exige aprovação explícita do dono, estão em `CLAUDE.md` e em `docs/agent/`.

---

## Changelog

As mudanças do projeto são registradas em `changelog.d/` e compiladas com [towncrier](https://towncrier.readthedocs.io/). Para gerar o changelog:

```bash
towncrier build --draft    # prévia sem alterar arquivos
towncrier build            # gera e atualiza CHANGELOG.md
```
