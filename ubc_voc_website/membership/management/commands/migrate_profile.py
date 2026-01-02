from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from membership.models import Profile

import csv
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help="Migrate Profiles form CSV"

    def handle(self, *args, **kwargs):
        path = "profile.csv"

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=["id", "firstname", "lastname", "phone", "blurb", "birthdate", "acc", "studentnumber", "vocene", "emergency_info", "spot_url", "trip_email", "pronouns"])

            for row in reader:
                user = User.objects.get(old_id=int(row['id']))

                if not user:
                    self.stdout.write(self.style.WARNING(f"User not found for old_id {int(row['id'])}"))
                else:
                    profile, created = Profile.objects.get_or_create(
                        user=user,
                        defaults={
                            'first_name': row['firstname'],
                            'last_name': row['lastname'],
                            'phone': row['phone'],
                            'birthdate': datetime.strptime(row['birthdate'], "%Y-%m-%d").date() if (row['birthdate'] and row['birthdate'] != "0000-00-00") else None
                        }
                    )
                    profile.pronouns = row['pronouns']
                    profile.student_number = row['student_number']
                    profile.bio = row['blurb']
                    profile.emergency_info = row['emergency_info']
                    profile.inreach_address = row['spot_url']
                    profile.acc = row['acc'] == "1"
                    profile.vocene = row['vocene'] == "1"
                    profile.trip_org_email = row['trip_email'] == "1"

                    if not created:
                        profile.first_name = row['firstname']
                        profile.last_name = row['lastname']
                        profile.phone = row['phone']
                        profile.birthdate = row['birthdate']

                    profile.save()

                    if created:
                        self.stdout.write(self.style.SUCCESS(f"Created profile for user {user.email}"))
                    else:
                        self.stdout.write(f"Profile for user {user.email} already exists")

            self.stdout.write(self.style.SUCCESS("Profile migration complete"))