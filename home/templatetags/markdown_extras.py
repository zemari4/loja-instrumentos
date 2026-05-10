import markdown as md
from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def render_md(value):
    """Convert markdown text to safe HTML (inline elements only)."""
    if not value:
        return ""
    return mark_safe(md.markdown(value, extensions=["nl2br"]))
