# Adotar Spec Driven Development com a issue do GitHub como spec

## Status

proposed (issue #34). Passa a `accepted` quando o dono aprovar.

## Decisão

O projeto adota Spec Driven Development nos moldes do GerenciaLume, com estas escolhas:

1. **A spec é a issue do GitHub** (`O que construir`, `Critérios de aceite`, `Fora de escopo`, `Bloqueada por`, `Pai`). Mudança grande ganha um PRD em `docs/prd/<slug>/PRD.md`, que se divide em issues.
2. **O dono aprova** spec, plano técnico, decisões de arquitetura e o merge. A IA rascunha, executa e revisa.
3. **Ciclo por issue:** branch `<tipo>/<nº>-<slug>`, TDD em seams combinados, review em dois eixos (padrões e spec) com triagem, fragmento de changelog, gate de conclusão verde, merge commit.
4. **`CLAUDE.md` é um roteador**; as regras ficam em `docs/agent/`, o vocabulário em `CONTEXT.md` e as decisões em `docs/adr/`.
5. **Skills globais** (`implement-pt`, `tdd-pt`, `code-review-pt`, `codebase-design-pt`) servem a este projeto e ao GerenciaLume, e leem as regras de cada repositório.
6. **Regras de código** para código novo: views delegam, regra em `services.py`, leitura complexa em `selectors.py`, dado de cliente sempre filtrado pelo dono.
7. **Automação mínima:** hook de nome de branch, `towncrier check` e Ruff com cobertura mínima na CI.

## Contexto

O GerenciaLume (CMMS do mesmo dono) já usa o método. O dono quer o mesmo modo de trabalho aqui, participando das decisões importantes em vez de deixar tudo para a IA.

O que funciona de fato no GerenciaLume: roteador `CLAUDE.md`, glossário com `_Avoid_`, ADRs curtos, issue com critérios de aceite, TDD com review em dois eixos e um gate de conclusão objetivo. O que ficou abandonado ou pesado: BDD em Gherkin (uma só feature, tudo `@pendente`), mapa de cobertura sincronizado por lint, diagramas com hook de regeneração, verify em instância isolada, trilhas por issue e partes específicas do produto (offline/PWA).

Este projeto é pessoal e menor, então o método entra enxuto. As alternativas consideradas para a fonte da spec foram arquivos em `docs/specs/` (descartada: diverge do GerenciaLume e duplica o que a issue já faz) e Gherkin (descartada: não pegou na prática).

## Consequência

- Todo trabalho começa numa issue com critérios verificáveis, e cada critério vira um teste.
- Fica mais fácil rastrear: o número da issue liga branch, commit, PR e changelog.
- O custo é escrever e aprovar a spec antes de codar. Correção trivial e ajuste de texto ficam fora disso.
- O dono precisa manter o `CONTEXT.md` e os ADRs, que são a memória do projeto.

### Fora do escopo por ora

Partes do GerenciaLume que **não** entram, com o gatilho para reconsiderar:

| Item | Gatilho para entrar |
|---|---|
| Mapa de cobertura e índice de funcionalidades sincronizados por lint | Testes duplicados ou funcionalidade sem teste descobertos mais de uma vez |
| Guarda automática contra teste que passa sem asserção ou com `skip` silencioso | O primeiro teste que passou sem verificar nada |
| Diagramas de arquitetura com hook | Uma segunda pessoa entrando no projeto, ou mais de ~10 apps |
| Verify em instância isolada, com evidência | Checkout real (pagamento de verdade) em produção |
| BDD em Gherkin com papel de PO | Um PO separado de quem implementa |
| Playwright e testes de ponta a ponta | Decisão registrada em ADR (ver `docs/adr/README.md`) |
