from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand
from django.db.models import Prefetch
from django.utils import timezone

from membership.models import Membership
from ubc_voc_website.utils import mailchimp_sync_user

from mailchimp3 import MailChimp

User = get_user_model()

class Command(BaseCommand):
    help="Sync member list to VOCene MailChimp list"

    def handle(self, *args, **kwargs):
        mailchimp_client = MailChimp(mc_api=settings.MAILCHIMP_API_KEY)
        mailchimp_list_id = settings.MAILCHIMP_LIST_ID

        users = User.objects.select_related("profile").prefetch_related(
            Prefetch(
                "membership_set", 
                queryset=Membership.objects.filter(active=True, end_date__gte=timezone.localdate()),
                to_attr="active_memberships"
            )
        )
        for user in users:
            self.stdout.write(f"Syncing user {user.email}")

            vocene = getattr(user.profile, "vocene", False)
            is_member = len(user.active_memberships) > 0

            mailchimp_sync_user(user, mailchimp_client, mailchimp_list_id, (vocene and is_member))

        self.stdout.write(self.style.SUCCESS("MailChimp sync complete"))