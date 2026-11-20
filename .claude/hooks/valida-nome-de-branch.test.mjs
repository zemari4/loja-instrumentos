// Testes do hook de nome de branch. Rodar com: node --test .claude/hooks/
import { test } from "node:test"
import assert from "node:assert/strict"
import { avalia, branchesCriadas } from "./valida-nome-de-branch.mjs"

const bash = (command) => avalia({ tool_name: "Bash", tool_input: { command } })
const worktree = (name) => avalia({ tool_name: "EnterWorktree", tool_input: { name } })

const aceitas = [
  "git checkout -b fix/19-login-email-duplicado",
  "git switch -c feat/34-exemplo origin/main",
  "git branch docs/34-implantar-sdd",
  "git worktree add ../w -b chore/40-atualiza-dependencias",
]
const recusadas = [
  "git checkout -b minha-branch",
  "git switch -c fix/sem-numero",
  "git checkout -b Fix/19-Maiuscula",
  "git branch feature/19-tipo-fora",
  "cd x && git checkout -b ajuste",
]
const ignoradas = [
  "git checkout main",
  "git checkout -- arquivo.py",
  "git branch -d velha",
  "git branch -m novo-nome",
  "git branch --show-current",
  "git branch",
  "git status",
  "pytest -q",
]

for (const cmd of aceitas) {
  test(`aceita: ${cmd}`, () => assert.equal(bash(cmd), null))
}
for (const cmd of recusadas) {
  test(`recusa: ${cmd}`, () => assert.match(bash(cmd), /Nome de branch inválido/))
}
for (const cmd of ignoradas) {
  test(`ignora: ${cmd}`, () => {
    assert.deepEqual(branchesCriadas(cmd), [])
    assert.equal(bash(cmd), null)
  })
}

test("worktree aceita <nº>-<slug>", () => assert.equal(worktree("34-implantar-sdd"), null))
test("worktree aceita sem name (nome gerado)", () => assert.equal(worktree(undefined), null))
for (const nome of ["impl-34-sdd", "implantar-sdd", "34"]) {
  test(`worktree recusa: ${nome}`, () => assert.match(worktree(nome), /Nome de worktree inválido/))
}
