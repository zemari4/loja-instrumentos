# CONTEXT: Loja Instrumentos

Glossário de domínio e vocabulário canônico. Quando seu output nomear um conceito de domínio (título de issue, critério de aceite, nome de teste, proposta de refactor), use o termo **exatamente como definido aqui**, sem drift para sinônimos. As linhas `_Avoid_` listam o que não usar.

> **Status: rascunho para revisão do dono.** Gerado a partir dos modelos em `catalog/`, `orders/`, `authentication/` e `home/`. Os termos em `_Avoid_` são sugestões. Onde houver "A definir", a decisão é do dono.

Decisões de arquitetura ficam em `docs/adr/`. Este arquivo cresce quando um termo é efetivamente resolvido em conversa ou em issue.

Identificadores de código seguem o padrão atual (inglês: `Instrument`, `Order`). O vocabulário em português vale para specs, issues, interface e documentação. A coluna "No código" faz a ponte.

## Catálogo

**Instrumento** (`catalog.Instrument`):
Item à venda. Tem categoria, marca, nome, preço, estoque e imagens.
_Avoid_: "produto" em specs e issues novas (existe em nomes legados de views e URLs, como `ProductCreateView`); "item" (reservado para item do pedido).

**Categoria** (`catalog.Category`):
Agrupamento de instrumentos, por exemplo guitarras e baterias.

**Marca** (`catalog.Brand`):
Fabricante do instrumento.

**Preço original** (`Instrument.original_price`):
Preço de referência antes do desconto. Quando maior que o preço atual, a loja exibe o desconto em porcentagem (`discount_percent`).

**Ativo** (`Instrument.is_active`):
Instrumento visível e vendável. Inativo não é comprado.
Ao cliente, a interface diz que um instrumento desativado "não está mais disponível" (decisão do dono na issue #24). Em código, specs e issues, use "inativo" (`is_active`) e "sem estoque" (`stock = 0`) para não misturar os dois motivos.
_Avoid_: "publicado".

**Destaque** (`Instrument.is_featured`):
Instrumento promovido na vitrine.

**Visualizações** (`Instrument.views_count`):
Contador de acessos à página do instrumento, usado no painel.

**Imagem do instrumento** (`catalog.ProductImage`):
Foto do instrumento, até 5 por instrumento. Uma é a principal.

**Estoque** (`Instrument.stock`):
Quantidade disponível de um instrumento. Um instrumento com estoque zero fica "sem estoque" e não pode ser comprado.

**Movimentação de estoque** (`catalog.StockMovement`):
Registro de cada mudança de estoque, com tipo, quantidade, autor e observação. Os tipos são Reposição, Ajuste manual, Venda e Devolução.
_Avoid_: "log de estoque"; "ajuste" para qualquer movimentação (Ajuste manual é só um dos tipos).

**Parcelamento** (`Instrument.price_installment`):
Valor exibido como o preço dividido em 12. É apenas exibição, sem regra de pagamento.

## Compra

**Carrinho** (`cart.services`):
Instrumentos e quantidades que o cliente pretende comprar. Fica na **sessão**, não no banco. A quantidade nunca passa do estoque.
_Avoid_: "sacola", "cesta".

**Checkout**:
Etapa em que o cliente informa o endereço de entrega e cria o pedido.

**Pedido** (`orders.Order`):
Compra confirmada de um cliente, com endereço de entrega e total calculado no momento do checkout.
_Avoid_: "ordem" (calque de _order_); "compra" (é a ação do cliente, não o registro).

**Item do pedido** (`orders.OrderItem`):
Linha de um pedido: instrumento, quantidade e preço no momento da compra.

**Status do pedido** (`Order.STATUS_*`):
Pendente, Pago, Enviado, Entregue, Cancelado. Todo pedido nasce Pendente.

**Pagamento** (`orders.Payment`):
Registro de pagamento de um pedido, com método e status. Hoje é **simulado**: não há gateway.

**Método de pagamento** (`Payment.METHOD_CHOICES`):
Cartão de crédito, PIX ou boleto.

**CEP** (`Order.shipping_cep`):
Código postal do endereço de entrega, no formato `00000-000`.

## Pessoas e acesso

**Cliente** (`auth.User` sem `is_staff`):
Quem compra. Só enxerga os próprios pedidos e dados.
_Avoid_: "usuário" quando o sentido for comprador ("usuário" é qualquer conta, inclusive staff); "customer" em texto de interface.

**Perfil** (`authentication.UserProfile`):
Dados extras do cliente: telefone, CPF (cifrado) e avatar.

**Histórico de login** (`authentication.LoginHistory`):
Registro de cada tentativa de login, com IP, navegador e sucesso ou falha.

**Manager** (app `manager`, rota `/manager/`):
Painel administrativo da loja, para staff. Gerencia estoque, imagens, pedidos, clientes, carrossel e métricas.
_Avoid_: "backstage" (nome antigo, removido do projeto); "admin" (é outra coisa).

**Admin** (`/admin/`):
Interface administrativa nativa do Django, com tema Jazzmin. Distinta do Manager.

## Vitrine

**Carrossel** (`home.CarouselSlide`):
Faixa de banners da página inicial, gerenciada no Manager. Cada banner é um **slide**.

## Termos a definir

- **Cancelamento:** quem pode cancelar, até quando e o que acontece com o estoque. A definir.
- **Devolução:** existe como tipo de movimentação de estoque, mas não há fluxo de devolução de pedido. A definir.
- **Frete:** não há cálculo nem cobrança. A definir junto com a escolha do serviço.
- **Instrumento vs produto:** confirmar se "Instrumento" será o único termo, ou se "produto" fica na interface do Manager.
