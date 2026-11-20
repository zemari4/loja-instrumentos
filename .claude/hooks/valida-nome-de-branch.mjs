#!/usr/bin/env node
// PreToolUse: recusa nome de branch/worktree fora da convenção de docs/agent/issue-tracker.md.
// Lê o JSON do hook no stdin; exit 2 recusa a chamada e devolve a mensagem ao agente.

export const BRANCH = /^(feat|fix|chore|docs|test|refactor)\/\d+-[a-z0-9]+(-[a-z0-9]+)*$/
export const WORKTREE = /^\d+-[a-z0-9]+(-[a-z0-9]+)*$/

const ORIENTACAO =
  "Convenção em docs/agent/issue-tracker.md (\"Nome de branch\"): branch = <tipo>/<nº-da-issue>-<slug> " +
  "(tipo: feat|fix|chore|docs|test|refactor; ex.: fix/19-login-email-duplicado); " +
  "name do EnterWorktree = <nº-da-issue>-<slug> (vira worktree-<nº>-<slug>)."

/** Nomes de branch que o comando cria (git checkout -b/-B, switch -c/-C, branch <nome>, worktree add -b). */
export function branchesCriadas(comando) {
  const nomes = []
  for (const trecho of comando.split(/&&|\|\||;|\n|\|/)) {
    const t = trecho.trim().split(/\s+/)
    if (t[0] !== "git") continue
    const args = t.slice(1).filter((a, i, todos) => !(a === "-C" || todos[i - 1] === "-C"))
    const [sub, ...resto] = args
    const depois = (flags) => {
      const i = resto.findIndex((a) => flags.includes(a))
      return i >= 0 ? resto[i + 1] : undefined
    }
    if (sub === "checkout") nomes.push(depois(["-b", "-B"]))
    else if (sub === "switch") nomes.push(depois(["-c", "-C", "--create"]))
    else if (sub === "worktree" && resto[0] === "add") nomes.push(depois(["-b", "-B"]))
    else if (sub === "branch") {
      const posicionais = resto.filter((a) => !a.startsWith("-"))
      const soCria = !resto.some((a) => /^-(d|D|m|M|c|C|l|a|r|v|u)|^--(delete|move|copy|list|all|remotes|set-upstream-to|unset-upstream|show-current|contains|merged|no-merged)/.test(a))
      if (soCria && posicionais[0]) nomes.push(posicionais[0])
    }
  }
  return nomes.filter(Boolean)
}

export function avalia({ tool_name, tool_input }) {
  if (tool_name === "EnterWorktree") {
    const nome = tool_input?.name
    if (nome === undefined || WORKTREE.test(nome)) return null
    return `Nome de worktree inválido: "${nome}". ${ORIENTACAO}`
  }
  if (tool_name === "Bash") {
    const ruins = branchesCriadas(tool_input?.command ?? "").filter((n) => !BRANCH.test(n))
    if (ruins.length) return `Nome de branch inválido: ${ruins.map((n) => `"${n}"`).join(", ")}. ${ORIENTACAO}`
  }
  return null
}

if (import.meta.url === `file://${process.argv[1]}`) {
  let entrada = ""
  process.stdin.on("data", (c) => (entrada += c))
  process.stdin.on("end", () => {
    let evento
    try {
      evento = JSON.parse(entrada)
    } catch {
      process.exit(0)
    }
    const recusa = avalia(evento)
    if (recusa) {
      console.error(recusa)
      process.exit(2)
    }
  })
}
