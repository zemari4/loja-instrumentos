# Estrutura do projeto

Monólito Django com templates server-side. Um app por área de negócio.

## Apps

| Pasta | Função | Camadas existentes |
|---|---|---|
| `backend/` | settings (`settings_base`, `_dev`, `_prod`, `_test`), urls, wsgi/asgi, storage | n/a |
| `home/` | página inicial e carrossel | models, views, services, tests |
| `authentication/` | login, cadastro, perfil, histórico de login, campo cifrado (`fields.py`) | models, forms, views, services, tests |
| `catalog/` | categorias, marcas, instrumentos, estoque, imagens | models, views, services, tests |
| `cart/` | carrinho, guardado na sessão | views, services, tests |
| `orders/` | pedidos, itens, pagamento (simulado), checkout | models, forms, views, services, tests |
| `manager/` | painel `/manager/` para staff: estoque, imagens, pedidos, clientes, carrossel, métricas | views, forms, mixins, tests |
| `dashboard/` | serviços de métricas, estoque e pedidos que alimentam o manager | services |
| `analytics/` | middleware de contexto de log e métricas | services |
| `musicmaisCSS/` | app do Tailwind (fonte CSS em `static_src`, CSS compilado em `static/css/dist`) | n/a |
| `theme/` | scaffolding do `django-tailwind` | n/a |

Não há `selectors.py` em nenhum app ainda (ver `conventions.md`).

## Outras pastas

| Pasta ou arquivo | O que é |
|---|---|
| `templates/` | Templates HTML de todos os apps, em `templates/<app>/` |
| `static/` | Imagens e assets estáticos |
| `docs/` | Documentação: `agent/` (regras para agentes), `adr/`, `prd/`, e as docs técnicas `orders-checkout.md` e `backstage-imagens-produto.md` |
| `changelog.d/` | Fragmentos do towncrier |
| `conftest.py` | Fixtures compartilhadas de teste |
| `pyproject.toml` | Configuração de pytest, cobertura, ruff, towncrier e bumpversion |
| `.github/workflows/ci.yml` | CI |
| `.claude/` | Hook de nome de branch e settings do projeto |
| `Dockerfile.dev`, `docker-compose.yml` | Ambiente de desenvolvimento em Docker |

## Fluxo de uma requisição

`backend/urls.py` → `urls.py` do app → view → form → service → model. As rotas públicas ficam na raiz (`""`); o painel em `/manager/`; o admin do Django em `/admin/`; o allauth em `/accounts/`.

## Settings

`backend/settings.py` escolhe o módulo por `DJANGO_ENV`: `prod` carrega `settings_prod`; qualquer outro valor carrega `settings_dev`. Testes usam `backend.settings_test`. O `.env` é lido por um loader próprio em `backend/settings.py`.
