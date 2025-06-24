from django import template
register = template.Library()

@register.filter
def priority_color(value):
    return {
        'H': 'danger',
        'M': 'warning',
        'L': 'secondary',
    }.get(value, 'light')
