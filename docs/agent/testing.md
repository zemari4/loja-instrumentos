# Testes e gate de conclusão

Receita única de verificação do projeto. Outros documentos apontam para cá em vez de repetir comandos.

## Pré-requisito: Redis

O cache é Redis em todos os ambientes (`docs/adr/0002-redis-como-cache-compartilhado.md`), então **a suíte precisa de um Redis acessível**. Os testes usam o banco 15 (`TEST_CACHE_LOCATION`) e limpam o cache antes de cada teste (`conftest.py`). Sem Redis, o `pytest` para cedo com uma mensagem que explica como subir um:

```bash
docker run -d --name loja-redis -p 127.0.0.1:6379:6379 redis:7-alpine
```

## Pirâmide

Prefira sempre o **tier mais baixo** que consiga validar o comportamento. Na dúvida entre dois, escolha o mais baixo.

| Tier | O que cobre | Como | Onde |
|---|---|---|---|
| Unidade e serviço | Regra de negócio em `services.py`, modelos, formulários, funções puras | `pytest`, com banco só quando o modelo precisa (`db`) | `<app>/tests/test_services.py`, `test_models.py`, `test_forms.py` |
| Integração de view | Rota, permissão, template, fluxo de sessão | `pytest` com `client` do pytest-django | `<app>/tests/test_views.py` |
| E2E no navegador | Fluxos críticos com várias telas | **Não existe hoje.** Playwright não está instalado. Só criar com um ADR que decida a ferramenta | (nenhum) |

Teste de view não deve repetir a regra que o teste do service já cobre: ele prova o encaixe (rota, permissão, template, redirecionamento).

## TDD obrigatório

Comece pelo teste que falha (`/tdd-pt`) em:

- Correção de bug: o teste reproduz o bug antes da correção.
- Regra de negócio nova ou alterada (service, modelo, cálculo, transição de status).
- Endpoint ou view nova.

Ajustes de texto, de estilo e de documentação não exigem TDD. Combine os **seams** (onde o comportamento é observado) com o dono antes de escrever teste.

## Cobertura mínima por tipo de mudança

| Mudança | Testes exigidos |
|---|---|
| Campo ou validação nova em modelo ou formulário | Um caso válido e um inválido |
| View ou endpoint novo | Sucesso, erro de entrada e permissão (anônimo, outro cliente, staff quando couber) |
| Regra de negócio em service | O caso comum e cada limite (estoque zero, quantidade acima do estoque, valores vazios) |
| Transição de status de pedido | Cada transição permitida e pelo menos uma proibida |
| Dado de cliente (pedido, perfil) | Teste de que **outro cliente não acessa** o dado |
| Upload | Tipo, tamanho e conteúdo inválidos |

Antes de criar um teste, procure se o comportamento já está coberto (`grep -ri "<tema>" */tests/`). Se estiver, estenda o teste existente.

## Dados de teste

- Use as fixtures de `conftest.py`: `session`, `user`, `category`, `brand`, `instrument`, `inactive_instrument`. Crie outras ali quando mais de um arquivo as usar.
- Gere valores aleatórios com **Faker** (`Faker("pt_BR")`), como já feito nos testes atuais. Dados pessoais de teste são sempre fictícios.
- Crie dados pelos services ou fixtures, evitando `Model.objects.create(...)` que produza um estado impossível em produção (pedido pago sem itens, instrumento com estoque negativo).
- Verifique o **estado persistido** (banco, sessão), não só o status HTTP.
- Sem estado compartilhado entre testes, e sem ordem implícita.
- Não use `sleep`. Para tempo, congele o relógio.
- Não esconda dívida com `pytest.skip` ou `xfail`: se precisar, escreva o motivo e a issue na própria linha.
- O pyproject usa `--reuse-db`. Depois de criar ou mudar uma migration, rode `pytest --create-db` uma vez.

## O que rodar quando

| Momento | Comandos |
|---|---|
| Durante o desenvolvimento | `pytest <arquivo> -q --tb=short` e `ruff check <arquivos>` com frequência |
| Ao concluir a funcionalidade | `pytest <app>/tests/ -k "<padrão>" -q --tb=short` e `ruff check .` |
| Antes do push | `pytest --cov=. --cov-report=term-missing`, `ruff check .` e conferir o fragmento de `changelog.d/` |
| Depois do push | A CI roda a suíte completa. Confira o resultado |

A suíte atual é pequena, então rodar tudo antes do push é aceitável. Se ela ficar lenta, rode só o app alterado e deixe o resto para a CI.

Saída enxuta para agentes: `pytest -q --tb=short` (os testes que passam não poluem o resultado).

## Gate de conclusão

Uma tarefa só está **completa** quando:

1. `ruff check .` passa.
2. `pytest` passa, com a cobertura no mínimo definido em `pyproject.toml` (`fail_under`).
3. Cada critério de aceite da issue tem um teste que o cobre.
4. Existe o fragmento `changelog.d/<nº-da-issue>.<tipo>.md`.
5. Depois do push, o workflow `CI` passa.

Se qualquer comando falhar, a tarefa **não está completa**. Informe o que falhou em vez de relaxar o teste, o limite de cobertura ou a CI.

## Na CI

O workflow `CI` (`.github/workflows/ci.yml`) roda em push e em PR para `main`:

| Passo | O que faz |
|---|---|
| Serviço | Redis 7 (`redis:7-alpine`) como `service` do job |
| Lint | `ruff check .` |
| Testes | `pytest` com cobertura mínima |
| Hook de branch | `node --test .claude/hooks/valida-nome-de-branch.test.mjs` |
| Changelog | `towncrier check --compare-with origin/main` (só em PR) |
