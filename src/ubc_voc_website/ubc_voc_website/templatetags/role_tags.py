from django import template
from datetime import datetime
from membership.models import Exec, Membership, PSG

register = template.Library()

@register.filter(name='is_member')
def is_member(user):
    memberships = Membership.objects.filter(
        user=user, 
        end_date__gte=datetime.now(),
        active=True    
    )
    if memberships.count() == 1:
        return True
    else:
        return False

@register.filter(name='is_exec')
def is_exec(user):
    exec_positions = Exec.objects.filter(user=user)
    if exec_positions.count() >= 1:
        return True
    else:
        return False

@register.filter(name='is_psg')
def is_psg(user):
    psg_positions = PSG.objects.filter(user=user)
    if psg_positions.count() >= 1:
        return True
    else:
        return False


