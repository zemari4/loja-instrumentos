# Convenções de código

Regras para **código novo**. Código antigo que não segue uma regra migra quando for tocado por uma issue, não em refactor em massa.

## Camadas

```
template / URL  →  view  →  form (entrada)  →  service (regra e escrita)  →  models / banco
                                              └→  selector (leitura complexa)
```

| Camada | Responsabilidade | Não faz |
|---|---|---|
| **View** (`views.py`) | Autoriza, valida com um Form, chama o service, devolve resposta | Regra de negócio, `Model.objects.*` com lógica, cálculo |
| **Form** (`forms.py`) | Contrato de entrada: campos, validação, mensagens | Acesso a outros modelos além do necessário para validar |
| **Service** (`services.py`) | Regra de negócio e escrita. Usa `transaction.atomic` quando altera mais de uma tabela | Conhecer `request`, template ou HTTP |
| **Selector** (`selectors.py`) | Leitura complexa (joins, agregações, filtros reutilizados). Ainda não existe em nenhum app: crie no app que precisar | Escrever no banco |
| **Model** | Campos, constraints, propriedades simples | Regra que envolve outro agregado |

Hoje existem `services.py` em `analytics`, `authentication`, `cart`, `catalog`, `home` e `orders`. Siga o padrão deles.

Quando o service precisa saber quem faz a ação, **receba o usuário como parâmetro explícito**, como em `orders.services.get_user_orders(user)` e `get_order_detail(user, pk)`. Services não leem `request`.

## Dono em toda query

Esta é a versão deste projeto da regra de isolamento por tenant do GerenciaLume.

- Todo dado de cliente (pedidos, perfil, endereço, histórico de login) é filtrado pelo dono na camada de service ou selector. Nunca confie só na URL.
- Para acesso por `pk` de outro cliente, devolva "não encontrado" (404), não "proibido", para não revelar que o registro existe.
- Rotas do `/manager/` exigem `is_staff`, via `BackstagePermissionMixin` (nome legado do termo "backstage"; renomeie para `ManagerPermissionMixin` quando tocar no arquivo).
- Todo dado de cliente novo precisa de um teste de que **outro cliente não o acessa** (`testing.md`).

## Contrato antes do código

Antes de uma view ou endpoint novo, a issue define: entrada (campos e validação), saída, quem pode acessar e os casos de erro. Esses itens viram o Form, os testes de permissão e os critérios de aceite. Contratos que outras partes consomem (por exemplo, respostas parciais do HTMX) ficam documentados em `docs/`.

## Migrations

- `python manage.py makemigrations` gera a migration, e ela é **revisada e commitada junto** com a mudança de modelo.
- **Nunca edite uma migration já aplicada** (em `main` ou em qualquer ambiente). Crie outra.
- Migration que altera ou apaga dado existente exige aprovação do dono e um plano de reversão na issue.

## Segurança e dados pessoais

- CPF vai em `EncryptedCharField` (Fernet, `FIELD_ENCRYPTION_KEY`). Nunca grave dado cifrável em texto puro.
- Valide upload no servidor (tipo, tamanho e conteúdo). Conteúdo vindo de usuário que vira HTML passa por sanitização (`bleach`).
- Rotas sensíveis (login, cadastro) usam `django-ratelimit`.
- Dados pessoais (CPF, e-mail, endereço) nunca aparecem em log, em exemplo de documentação ou em fixture com dado real.
- Mudança nessas áreas exige aprovação explícita do dono (`CLAUDE.md`).

## Frontend

- Templates em `templates/<app>/`. Estilo com Tailwind (compilado em `musicmaisCSS/static_src`) e componentes do DaisyUI.
- Interação parcial com HTMX (`hx-*`, `django-htmx`) e interações locais com Alpine.js (`x-data`).
- Não use o Tailwind Play CDN em páginas novas: a decisão sobre as páginas existentes está em aberto (ver `docs/adr/README.md`).
- Texto de interface em português do Brasil, seguindo `CONTEXT.md`.

## Nomes

- Identificadores de código em inglês, no padrão atual (`Instrument`, `Order`, `Payment`).
- Vocabulário de domínio em português em specs, issues, interface e docs, conforme `CONTEXT.md`. Não invente sinônimo: se faltar o termo, proponha-o no `CONTEXT.md`.
- Nomes de teste descrevem o comportamento esperado e seguem o idioma do arquivo.

## O que não fazer

- Não adicione dependência sem aprovação.
- Não crie abstração para uma única chamada. Reaproveite o que existe antes de criar.
- Não desative testes, não baixe o mínimo de cobertura e não relaxe a CI para fazer algo passar.
- Não commite `.env`, `db.sqlite3`, `media/` nem relatórios de segurança (já estão no `.gitignore`).
