from django.utils import timezone
from membership.models import Exec, Membership, PSG

def is_member(user):
    active_memberships = Membership.objects.filter(
            user=user,
            end_date__gte=timezone.localdate(),
            active=True
        )
    return active_memberships.count() == 1

def is_exec(user):
    if user.is_superuser:
        return True
    exec_positions = Exec.objects.filter(user=user)
    return exec_positions.count() >= 1

def is_PSG(user):
    psg_positions = PSG.objects.filter(user=user)
    return psg_positions.count() >= 1