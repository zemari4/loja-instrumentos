# Domínio e decisões

Antes de explorar o código ou propor uma mudança de domínio, leia:

1. **`CONTEXT.md`**: vocabulário canônico, com os termos a evitar. Use os termos exatamente como definidos. Se o conceito novo não está lá, proponha a entrada em vez de inventar um nome.
2. **`docs/adr/`**: decisões já tomadas na área que você vai mexer.

## Quando a spec contradiz uma decisão registrada

Se o trabalho pedido conflita com um ADR, **não implemente em silêncio**. Sinalize explicitamente, por exemplo:

> _Contradiz o ADR 0003 (mídia em disco), mas vale reabrir porque..._

e deixe o dono decidir se reabre o ADR (novo ADR que substitui o antigo) ou ajusta a spec.

## Quando um termo está em "A definir"

Itens em "Termos a definir" do `CONTEXT.md` (cancelamento, devolução, frete) ainda não têm regra. Uma issue que dependa deles precisa primeiro resolver o termo com o dono. Não escolha o comportamento por conta própria.

## O que está e o que não está implementado

- **Pagamento é simulado.** Não há gateway real.
- Frete, nota fiscal, Redis, Celery, Sentry e S3 não têm código (só variáveis no `.env.example`).
- A lista atualizada está no `README.md`, seção "Ainda não implementado".
