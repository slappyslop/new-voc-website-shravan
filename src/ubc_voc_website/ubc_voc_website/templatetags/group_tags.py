from django import template
from django.contrib.auth.models import Group

register = template.Library()

@register.filter(name='is_member')
def is_member(user):
    return user.groups.filter(name="Members").exists()

@register.filter(name='is_exec')
def is_exec(user):
    return user.groups.filter(name="Exec").exists()


@register.filter(name='is_psg')
def is_psg(user):
    return user.groups.filter(name="PSG").exists()


