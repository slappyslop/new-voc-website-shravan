from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.crypto import get_random_string
import csv

User = get_user_model()

class Command(BaseCommand):
    help="Migrate Users from CSV"

    def handle(self, *args, **options):
        path="user.csv"

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=["id", "email"])

            for row in reader:
                user, created = User.objects.get_or_create(
                    email=row['email'].strip(),
                    defaults={
                        'old_id': int(row["id"]),
                        'is_active': True
                    }
                )
                if created:
                    user.set_password(get_random_string(20))
                    user.save()
                    self.stdout.write(self.style.SUCCESS(f"Created user {user.email}"))
                else:
                    self.stdout.write(f"User {user.email} already exists")

        self.stdout.write(self.style.SUCCESS("User migration complete"))        