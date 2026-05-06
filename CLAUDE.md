# CLAUDE.md — Music Mais

E-commerce de instrumentos musicais: catálogo, carrinho, checkout, pedidos e painel administrativo.

**Stack**: Django · TailwindCSS · HTMX · Flowbite · Alpine.js · DaisyUI · Celery · Redis

---

## Checklist obrigatório por tarefa

**TODA tarefa DEVE seguir estes passos, sem exceção:**

1. **Implementar** a funcionalidade, levantando hipóteses de teste durante o desenvolvimento
2. **Criar testes** em `<app>/tests/` cobrindo o que foi implementado
3. **Rodar testes** — `pytest <app>/tests/ -x` deve passar sem erros
4. **Criar fragmento towncrier** em `changelog.d/` — criar **durante** a implementação, não postergar
5. **Documentação** (se aplicável) — criar ou atualizar arquivo em `docs/`

IMPORTANTE: nunca finalizar tarefa sem testes E fragmento towncrier.

---

## Convenções de código

- **Sempre CBVs** — `ListView`, `DetailView`, `TemplateView`, etc. Nunca FBVs
- **Templates** ficam em `/templates/<app>/` na raiz. Nunca dentro de apps
- **Interatividade**: HTMX + Alpine.js + Flowbite/DaisyUI. Nunca JS customizado
- **DRF/serializers** apenas para APIs REST reais, nunca para páginas HTML
- **Imports** no topo do arquivo. Exceção: dentro de funções para evitar circular imports
- **Services**: lógica de negócio em `<app>/services/`, views finas (orquestração)
- **Modelos**: `created_at`/`modified_at`, `simple_history` nos críticos (pedidos, pagamentos, estoque). Criar migrações ao alterar

---

## Testes

- Abordagem **pragmática**: implementar primeiro, depois testar o comportamento
- Testes em `<app>/tests/` (nunca na raiz, nunca `<app>/tests.py`)
- **pytest style** com fixtures definidas no conftest raiz
- Testar **lógica de negócio**, não o framework
- Mockar apenas **fronteiras externas** (APIs de pagamento, email, S3), nunca código interno

```bash
pytest                              # todos os testes
pytest <app>/tests/ -x              # testes de um app
pytest --cov=. --cov-report=term-missing  # com cobertura
```

---

## Branches e workflow Git

Padrão: `<tipo>-<número>/<descrição-curta>` (ex: `feat-12/sistema-carrinho`)

- Tipos: `feat`, `fix`, `chore`, `style`, `perf`, `docs`, `test`
- Sempre criar a partir de `main` sincronizada
- Usar **`/branch`** para criar, **`/commit`** para commitar, **`/pr`** para PR
- Branches pequenas e focadas. Trabalho fora do escopo vai para branch separada

---

## Changelog (towncrier)

Fragmentos em `changelog.d/<nome-com-hifens>.<tipo>.md`

| Tipo | Uso |
|------|-----|
| `feature` | Nova funcionalidade |
| `bugfix` | Correção de bug |
| `improvement` | Melhoria em algo existente |
| `removal` | Remoção de funcionalidade |
| `doc` | Documentação |
| `misc` | Sem entrada no changelog (refactor, CI) |

Conteúdo: uma frase amigável descrevendo **o que mudou para o usuário**, sem jargão técnico. Começar com verbo no presente.

---

## Skills obrigatórias

| Skill | Quando usar |
|-------|-------------|
| `/branch` | Sempre que criar uma nova branch |
| `/commit` | Sempre que criar um commit |
| `/pr` | Sempre que criar um pull request |

---

## Comandos essenciais

```bash
source .venv/bin/activate                     # ativar venv
python manage.py runserver                    # servidor dev
cd theme/static_src && npm run watch          # tailwind watch
python manage.py makemigrations && python manage.py migrate  # migrações
celery -A musicmais worker -l info -E         # celery worker
```

---

## Documentação técnica (`docs/`)

Funcionalidades completas devem ter documentação em `docs/`. Ao alterar lógica de uma funcionalidade já documentada: ler antes, atualizar depois. Formato obrigatório no topo:

```markdown
# Nome — Documentação Técnica
> **Última atualização**: YYYY-MM-DD | **Versão do sistema**: X.Y.Z
```

---

## Regras críticas

- Nunca criar novo app sem perguntar ao usuário
- Nunca editar `CHANGELOG.md` diretamente — usar towncrier
- Nunca usar estilos inline (`style="..."`) em templates — usar Tailwind
- Nunca usar comentários HTML (`<!-- -->`) em templates — usar `{# #}` ou `{% comment %}`
- Nunca usar valores arbitrários de tamanho (`text-[13px]`, `h-[200px]`) — usar classe padrão mais próxima
- Nunca finalizar tarefa sem testes e fragmento towncrier
