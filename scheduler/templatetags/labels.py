from django import template
from django.utils.safestring import mark_safe

register = template.Library()

primary = '<span class="badge badge-primary">{}</span>'
secondary = '<span class="badge badge-secondary">{}</span>'
success = '<span class="badge badge-success">{}</span>'
danger = '<span class="badge badge-danger">{}</span>'
warning = '<span class="badge badge-warning">{}</span>'
info = '<span class="badge badge-info">{}</span>'
light = '<span class="badge badge-light">{}</span>'
dark = '<span class="badge badge-dark">{}</span>'

mapping = {
    'running': primary,
    'error': danger,
    'ready': success,
    'outdated': warning,
    'done': success,
}


@register.filter(is_safe=True)
def label(value):
    return mark_safe(mapping.get(value.lower(), primary).format(value))
