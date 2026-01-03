from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from membership.models import Membership

import csv
from datetime import datetime

User = get_user_model()

MEMBERSHIP_TYPE_MAPPINGS = {
    "1": Membership.MembershipType.REGULAR,
    "2": Membership.MembershipType.ASSOCIATE,
    "3": Membership.MembershipType.ACTIVE_HONORARY,
    "4": Membership.MembershipType.ASSOCIATE,
    "5": Membership.MembershipType.ACTIVE_HONORARY
}

class Command(BaseCommand):
    help="Migrate Memberships from CSV"

    def handle(self, *args, **kwargs):
        path = "memberships.csv"

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=["member_id", "startdate", "enddate", "type_id", "active"])

            for row in reader:
                try:
                    user = User.objects.get(old_id=int(row["member_id"]))
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"User not found for old_id {int(row["member_id"])}"))
                    continue

                membership, created = Membership.objects.get_or_create(
                    user=user,
                    start_date=datetime.strptime(row['startdate'], "%Y-%m-%d").date(),
                    defaults={
                        'end_date': datetime.strptime(row['enddate'], "%Y-%m-%d").date(),
                        'type': MEMBERSHIP_TYPE_MAPPINGS[row['type_id']]
                    }
                )

                membership.save()

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created membership with start {row['startdate']} for user {user.email}"))
                else:
                    self.stdout.write(f"Membership with start {row['startdate']} for user {user.email} already exists")

            self.stdout.write(self.style.SUCCESS(f"Membership migration complete"))
