# Issue tracker: GitHub Issues

As issues deste projeto ficam no GitHub, em `zemari4/loja-instrumentos`, e são manipuladas pela CLI `gh`.

**A issue é a spec.** Ela descreve o que construir e os critérios de aceite. Uma mudança grande ganha também um PRD em `docs/prd/<slug>/PRD.md`, e cada fatia implementável vira uma issue.

## Convenções

- PRDs ficam no repositório (`docs/prd/`). Só unidades implementáveis de trabalho viram issue.
- O estado de triagem é a label da própria issue (ver `triage-labels.md`).
- Conversas e decisões vão como comentário na issue (`gh issue comment`).
- Uma issue filha aponta a mãe em `## Pai`, com o número (ex.: `#70`).
- Corpo da issue em português, com os cabeçalhos `## O que construir`, `## Critérios de aceite`, `## Fora de escopo`, `## Bloqueada por` e, quando houver, `## Pai`. O template está em `.github/ISSUE_TEMPLATE/fatia.md`.
- Cada critério de aceite é verificável e vira um teste (ver `testing.md`).

## Nome de branch

Branch que resolve uma issue: `<tipo>/<nº-da-issue>-<slug>`, com tipo em `feat|fix|chore|docs|test|refactor` e slug em minúsculas, com hífens e sem acento (ex.: `fix/19-login-email-duplicado`).

Worktree (`EnterWorktree`): o `name` é `<nº-da-issue>-<slug>`, e a branch sai como `worktree-<nº>-<slug>`.

O número da issue no nome não é enfeite: liga branch, commit, PR e fragmento de changelog. Um hook `PreToolUse` (`.claude/hooks/valida-nome-de-branch.mjs`) recusa nomes fora desse padrão em `git checkout -b`, `git switch -c`, `git branch <nome>`, `git worktree add -b` e `EnterWorktree`.

Nunca trabalhe direto na `main`: crie a branch antes de alterar arquivos.

## Commits

`tipo(escopo): descrição no imperativo, em português (#nº)`

- Tipos: os mesmos da branch.
- Escopo é o app ou a área (`orders`, `catalog`, `manager`, `ci`, `docs`). Pode ser omitido quando a mudança atravessa vários.
- Exemplos: `fix(auth): recusa login por e-mail duplicado (#19)`, `docs: adiciona ADR do método SDD (#34)`.

## Pull request

- Um PR por issue, a partir da branch da issue, contra `main`.
- Título no mesmo formato do commit. Corpo com `Closes #<nº>`, o que mudou, como foi verificado e o que ficou fora.
- Entra por **merge commit** (sem squash), como no histórico atual. O dono faz o merge.
- Só entra com o gate de conclusão verde (`testing.md`) e o fragmento de changelog presente.

## Fragmento de changelog

`changelog.d/<nº-da-issue>.<tipo>.md`, com tipo entre `feature`, `bugfix`, `improvement`, `removal` e `doc`. Uma frase, no ponto de vista de quem usa. O `towncrier check` na CI exige o fragmento em PR de mudança de código.

## Quando uma skill diz "publicar no issue tracker"

Crie a issue com `gh issue create --repo zemari4/loja-instrumentos --title "..." --label "..." --body-file <arquivo>`, usando o template de `fatia.md`, e aplique as labels de `triage-labels.md`.

## Quando uma skill diz "buscar a issue"

Use `gh issue view <nº> --repo zemari4/loja-instrumentos`. O dono normalmente passa o número direto.

## Observação sobre o ambiente do agente

Os comandos `gh` de **escrita** (criar issue, label ou PR) falham de forma **intermitente** com `Post ".../graphql": unexpected EOF`, enquanto as leituras funcionam. No piloto (#24 e #26) isso ocorreu dentro e fora do sandbox, então não é só o sandbox. Conduta:

1. **Antes de repetir, confira se o recurso já existe** (`gh issue list`, `gh pr list --head <branch>`): a chamada pode ter falhado depois de criar. Isso evita issue ou PR duplicado.
2. Repita até 3 vezes. Se continuar falhando, peça ao dono para rodar o comando com `!` no prompt.
3. Se a falha vier só dentro do sandbox, peça ao dono para autorizar a repetição fora dele. Não tente contornar de outro jeito.
4. `gh run view --log-failed` pode devolver `403`. Nesse caso, veja o passo que falhou em `gh run view <id>` e reproduza o problema localmente.

## Limpeza de branches

Depois do merge, apague a branch local e a remota. Só apague a que cumpre **as duas** condições: PR mergeado (`gh pr list --state merged --json headRefName`) e ponta já dentro da `main` (`git branch -r --merged origin/main`). Nunca apague `main` nem `homolog`. Para apagar em lote, peça o aval do dono.
