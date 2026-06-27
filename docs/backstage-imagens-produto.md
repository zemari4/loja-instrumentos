# Imagens de Produto no Backstage — Documentação Técnica
> **Última atualização**: 2026-05-08 | **Versão do sistema**: 0.1.0

## Visão geral

O manager permite gerenciar até **5 fotos por produto** diretamente na página de edição do produto (`/manager/estoque/<pk>/produto/`). As imagens são armazenadas em `media/products/` e servidas via `MEDIA_URL`.

---

## Modelo

`catalog.models.ProductImage`

| Campo | Tipo | Descrição |
|-------|------|-----------|
| `instrument` | FK → Instrument | Produto ao qual a imagem pertence |
| `image` | ImageField | Arquivo em `media/products/` |
| `is_main` | BooleanField | Se `True`, é a imagem exibida na listagem e no card do catálogo |
| `order` | PositiveSmallIntegerField | Ordem de exibição (ascendente) |
| `created_at` | DateTimeField (auto_now_add) | Registra quando a imagem foi enviada |

**Índice**: composto em `(instrument_id, is_main)` — acelera `filter(is_main=True)` usado pela property `main_image`.

A property `Instrument.main_image` retorna o `ImageFieldFile` da imagem marcada como principal; se nenhuma tiver `is_main=True`, usa a primeira por `order`.

---

## URLs e views

Todas as rotas ficam no namespace `manager` (prefixo `/manager/`).

| URL | View | Descrição |
|-----|------|-----------|
| `estoque/<pk>/imagens/upload/` | `ProductImageUploadView` | Upload de 1–5 imagens |
| `estoque/imagens/<image_pk>/excluir/` | `ProductImageDeleteView` | Remove imagem |
| `estoque/imagens/<image_pk>/principal/` | `ProductImageSetMainView` | Define como principal |

### Comportamento por tipo de requisição

Todas as três views detectam se a requisição veio do HTMX via `request.htmx` (middleware `django_htmx`):

- **HTMX**: retorna o partial `manager/partials/product_images.html` para atualização parcial da seção (`outerHTML` swap em `#product-images-section`)
- **POST nativo**: redireciona para `manager:inventory_update` com mensagem de sucesso via Django messages

---

## Upload

- Aceita múltiplos arquivos (`input[multiple]`) via `enctype="multipart/form-data"`
- Limite de **5 imagens por produto** — slots disponíveis = `MAX_PRODUCT_IMAGES - existing_count`
- A primeira imagem enviada para um produto sem fotos é automaticamente marcada como `is_main=True`
- Excedentes na mesma requisição são ignorados silenciosamente

### Constante relevante

```python
# manager/views/products.py
MAX_PRODUCT_IMAGES = 5
```

---

## Delete

- Remove o arquivo do filesystem (`image.image.delete(save=False)`) e o registro do banco
- Se a imagem removida era a principal, promove automaticamente a próxima por `order`
- Imagem inexistente retorna HTTP 204 (sem erro) em HTMX, redirect em POST nativo

---

## Template

O partial `templates/manager/partials/product_images.html` é incluído em `form.html` **fora** do `<form>` principal do produto para evitar nesting de forms HTML.

Interatividade:
- **Drag-and-drop e preview**: Alpine.js (`x-data`, `@drop`, `@change`)
- **Confirmação de exclusão**: Alpine.js `@click.prevent` com `form.requestSubmit()` (dispara o evento `submit` para o HTMX interceptar)
- **Upload**: form nativo `method="post" enctype="multipart/form-data"` (HTMX não é usado para upload de arquivos por limitações de serialização)

---

## Formato de preço (BRDecimalField)

O campo de preço usa `BRDecimalField` (em `manager/forms.py`), que sobrescreve `to_python()` para aceitar o formato brasileiro:

| Entrada | Interpretação |
|---------|---------------|
| `4.200,59` | R$ 4200,59 |
| `999,90` | R$ 999,90 |
| `4200.59` | R$ 4200,59 (formato padrão do banco) |
