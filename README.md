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

### Frontend (interface visual)

| Tecnologia | O que faz |
|---|---|
| **TailwindCSS** | Sistema de estilização que define cores, espaçamentos e layout das páginas |
| **DaisyUI** | Biblioteca de componentes visuais prontos (botões, cards, modais) construída sobre o Tailwind |
| **Flowbite** | Componentes interativos adicionais como dropdowns, tooltips e sidebars |
| **HTMX** | Permite atualizar partes da página sem recarregar tudo (ex: adicionar ao carrinho sem reload) |
| **Alpine.js** | Adiciona pequenas interações visuais diretamente nos elementos HTML (ex: abrir/fechar menus) |

### Qualidade e processo

| Ferramenta | O que faz |
|---|---|
| **pytest** | Roda os testes automatizados para garantir que o sistema funciona corretamente |
| **towncrier** | Gera o changelog (registro de mudanças) do projeto de forma organizada |
| **GitHub Actions** | CI/CD: roda os testes automaticamente a cada alteração no código |

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
└── docs/               # Documentação técnica das funcionalidades
```

---

## Como rodar localmente

### Pré-requisitos

- Python 3.12+ (exigido pelo `pyproject.toml` e pelo Django 6)
- Node.js — apenas se for recompilar o CSS; o projeto já vem com o CSS buildado

### Passos

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
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

## Changelog

As mudanças do projeto são registradas em `changelog.d/` e compiladas com [towncrier](https://towncrier.readthedocs.io/). Para gerar o changelog:

```bash
towncrier build --draft    # prévia sem alterar arquivos
towncrier build            # gera e atualiza CHANGELOG.md
```
