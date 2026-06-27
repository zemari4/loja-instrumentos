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
| **Celery** | Executa tarefas em segundo plano (ex: envio de e-mails, notificações) sem travar o site |
| **Redis** | Banco de dados em memória usado como fila de tarefas para o Celery e cache de dados frequentes |

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
musicmais/
├── authentication/   # Login, cadastro e conta do usuário
├── catalog/            # Catálogo de produtos
├── cart/               # Carrinho de compras
├── orders/             # Pedidos e histórico de compras
├── analytics/          # Métricas e dados da loja
├── home/               # Página inicial
├── templates/          # Templates HTML de todas as páginas
└── docs/               # Documentação técnica das funcionalidades
```

---

## Como rodar localmente

### Pré-requisitos

- Python 3.11+
- Redis instalado e rodando
- Node.js (para compilar o CSS)

### Passos

```bash
# 1. Clone o repositório
git clone <url-do-repositorio>
cd musicmais

# 2. Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
.venv\Scripts\activate           # Windows

# 3. Instale as dependências Python
pip install -r requirements.txt

# 4. Configure as variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações locais

# 5. Rode as migrações do banco de dados
python manage.py migrate

# 6. Inicie o servidor
python manage.py runserver
```

Em outro terminal, para compilar o CSS automaticamente:

```bash
cd theme/static_src && npm install && npm run watch
```

Para processar tarefas em segundo plano (opcional):

```bash
celery -A musicmais worker -l info -E
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
