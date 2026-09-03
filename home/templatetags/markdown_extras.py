import bleach
import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

# Subconjunto inline da whitelist de MARKDOWNIFY (settings_base.py). É mais
# estreita de propósito: este filtro renderiza título e subtítulo do carrossel,
# onde cabeçalhos, listas e blocos de código quebrariam o layout.
ALLOWED_TAGS = ["a", "b", "strong", "em", "i", "code", "br", "span"]
ALLOWED_ATTRS = {"a": ["href", "title"]}

# Sem esta restrição, [texto](javascript:...) continuaria sendo XSS mesmo com as
# tags sanitizadas — o padrão do bleach ainda aceitaria mailto e outros esquemas.
ALLOWED_PROTOCOLS = ["http", "https"]


@register.filter
def render_md(value):
    """Renderiza markdown como HTML, removendo qualquer marcação não permitida.

    O markdown puro não escapa HTML: sem o bleach.clean abaixo, o conteúdo
    passaria intacto para o navegador e mark_safe impediria o escape do template.
    """
    if not value:
        return ""
    html = md.markdown(value, extensions=["nl2br"])
    limpo = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRS,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    return mark_safe(limpo)
