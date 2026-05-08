# Checkout e Pedidos — Documentação Técnica
> **Última atualização**: 2026-05-08 | **Versão do sistema**: 0.1.0

## Visão geral

Fluxo de compra do usuário: carrinho → checkout com endereço → pedido criado → confirmação → histórico de pedidos. O pagamento é simulado (sem gateway real); a integração com gateway fica para etapa futura.

---

## Modelos

### `Order` — `orders.models`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `customer` | FK → User | Comprador |
| `status` | CharField | `pending` / `paid` / `shipped` / `delivered` / `cancelled` |
| `total_price` | DecimalField | Total calculado no momento do checkout |
| `shipping_name` | CharField | Nome do destinatário |
| `shipping_cep` | CharField(9) | CEP formatado como `00000-000` |
| `shipping_street` | CharField | Logradouro e número |
| `shipping_complement` | CharField | Complemento (opcional) |
| `shipping_neighborhood` | CharField | Bairro |
| `shipping_city` | CharField | Cidade |
| `shipping_state` | CharField(2) | UF (ex: SP) |
| `created_at` / `updated_at` | DateTimeField | Auditoria |

`Order` tem `simple_history` via `HistoricalRecords`.

### `OrderItem` — `orders.models`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `order` | FK → Order | Pedido pai |
| `instrument` | FK → Instrument | Produto vendido |
| `quantity` | PositiveIntegerField | Quantidade |
| `unit_price` | DecimalField | Preço no momento da venda (snapshot) |

Property `subtotal` = `unit_price × quantity`.

---

## URLs e views

Namespace: `orders` (prefixo raiz `""`).

| URL | View | Descrição |
|-----|------|-----------|
| `/checkout/` | `CheckoutView` | Resumo do carrinho + form de endereço |
| `/pedido/<pk>/confirmacao/` | `OrderConfirmView` | Confirmação pós-criação |
| `/minha-conta/pedidos/` | `OrderListView` | Histórico do usuário (paginado 10/pág) |
| `/minha-conta/pedidos/<pk>/` | `OrderDetailView` | Detalhe de um pedido |

Todas as views requerem autenticação (`LoginRequiredMixin`); unauthenticated → `/usuario/entrar`.

---

## Service: `orders.services`

### `create_order_from_cart(user, cart_session, address_data)`

Cria pedido a partir do carrinho de sessão. Fluxo dentro de `transaction.atomic()`:

1. Valida estoque de cada item com `select_for_update()` — lança `OutOfStockError` se insuficiente
2. Cria `Order` com `address_data` e total calculado pelo `cart_total()`
3. Cria um `OrderItem` por item do carrinho
4. Decrementa estoque via `Instrument.objects.filter(...).update(stock=F("stock") - qty)` (UPDATE atômico)
5. Limpa o carrinho com `clear_cart()`

Se qualquer etapa falhar, a transação faz rollback — nenhum dado parcial é salvo.

### `get_user_orders(user)` / `get_order_detail(user, pk)`

Filtram por `customer=user`, garantindo que cada usuário só acesse seus próprios pedidos.

---

## Form: `CheckoutForm`

Campos do endereço + `payment_method` (RadioSelect). Validações:
- `shipping_cep`: apenas dígitos, exatamente 8, normalizado para `00000-000`
- `shipping_state`: obrigatório (impede envio sem UF)

`form.address_data()` retorna o dicionário sem `payment_method`, pronto para `**kwargs` no service.

---

## Erros tratados

| Cenário | Comportamento |
|---------|---------------|
| Carrinho vazio ao acessar `/checkout/` | Redireciona para `/carrinho/` com mensagem de erro |
| Formulário inválido | Re-renderiza com erros inline |
| Estoque insuficiente no POST | Re-renderiza com mensagem de `OutOfStockError` |
| Pedido de outro usuário | HTTP 404 |
