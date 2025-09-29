from django import template

register = template.Library()

@register.filter
def clean_title(value):
    if ':' in value:
        return value.split(':', 1)[1].strip()
    return value
    