from django.contrib.auth import get_user_model
from django.utils import timezone

from membership.models import Exec, Membership, PSG

import hashlib

User = get_user_model()

def is_member(user):
    return Membership.objects.filter(
            user=user,
            end_date__gte=timezone.localdate(),
            active=True
        ).exists()

def is_exec(user):
    if user.is_superuser:
        return True
    exec_positions = Exec.objects.filter(user=user)
    return exec_positions.count() >= 1

def is_PSG(user):
    psg_positions = PSG.objects.filter(user=user)
    return psg_positions.count() >= 1

def mailchimp_sync_user(user, mailchimp_client, mailchimp_list_id, subscriber):
    subscriber_hash = hashlib.md5(user.email.lower().encode("utf-8")).hexdigest()
    if subscriber:
        mailchimp_client.lists.members.create_or_update(
            list_id=mailchimp_list_id,
            subscriber_hash=subscriber_hash,
            data={
                "email_address": user.email,
                "status_if_new": "subscribed",
                "status": "subscribed"
            }
        )
    else:
        try:
            mailchimp_client.lists.members.delete(
                list_id=mailchimp_list_id,
                subscriber_hash=subscriber_hash
            )
        except Exception:
            pass
    