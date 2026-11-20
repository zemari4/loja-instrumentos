# Labels

As skills falam em cinco papéis de triagem. Este arquivo mapeia cada papel para a label real do repositório (`gh label list --repo zemari4/loja-instrumentos`). Se criar uma label nova, atualize esta tabela no mesmo passo: ela é a fonte que os agentes consultam antes de rotular.

## Triagem (estado da issue)

| Papel | Label | Significado |
|---|---|---|
| `needs-triage` | (nenhuma) | Issue sem label de triagem está por triar |
| `needs-info` | `question` | Esperando informação de quem abriu |
| `ready-for-agent` | `ready-for-agent` | Totalmente especificada, pode ser implementada por agente |
| `ready-for-human` | `human-in-the-loop` | Exige implementação ou decisão humana |
| `wontfix` | `wontfix` | Não será feita |

## Prioridade

Ortogonal à triagem, em label própria:

- `prioridade:critica`: bloqueia o merge de outras mudanças.
- `prioridade:alta`
- `prioridade:media`
- `prioridade:baixa`

`tech-debt` marca refatoração sem urgência.

## Severidade (achados de segurança)

Já existentes, usadas pela auditoria de segurança: `seguranca`, `severidade:alta`, `severidade:media`, `severidade:baixa`. Severidade descreve o **risco do achado**; prioridade descreve a **ordem de trabalho**. Um achado pode ter as duas.

## Área

Já existentes: `auth`, `cart`, `orders`, `home`, `manager`, `upload`, `config`, `ci`, `xss`, `lgpd`, `repo`. Use a que corresponde ao app ou tema principal da issue. O escopo do commit usa o mesmo nome (`fix(auth): ...`).

## Tipo (padrão do GitHub)

`bug`, `enhancement`, `documentation`, `question`, `duplicate`, `invalid`, `good first issue`, `help wanted`.

## Labels a criar

`ready-for-agent`, `human-in-the-loop`, `tech-debt`, `prioridade:critica`, `prioridade:alta`, `prioridade:media` e `prioridade:baixa` ainda não existem no repositório. A criação é feita na issue #34.
