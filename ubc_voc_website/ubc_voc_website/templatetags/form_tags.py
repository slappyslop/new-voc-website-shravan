from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def render_form_field(field):
    required = "<span class='text-danger'>*</span>" if field.field.required else ""
    errors = "".join([f"<div class='text-danger'>{e}</div>" for e in field.errors])

    html = f"<div class='mb-4'><label for='{field.id_for_label}'>{field.label}{required}:&nbsp;</label>{field}{errors}</div>" 
    return mark_safe(html)