"""
SELECT id, memberid, outdate, duedate, returndate, what, deposit, notes, extensions, appropriated, type, qmname FROM `gear`
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from gear.models import Rental, RentalTypes

import csv
from datetime import datetime, timedelta
import re

User = get_user_model()

class Command(BaseCommand):
    help="Migrate gearmaster entries from CSV"

    def handle(self, *args, **kwargs):
        path = "gear.csv"

        def parse_deposit(deposit):
            if deposit is None:
                return 0
            
            deposit = str(deposit).strip()
            deposit = re.search(r"-?\d+", deposit)
            return int(deposit.group()) if deposit else 0

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=[
                "id",
                "memberid",
                "outdate",
                "duedate",
                "returndate",
                "what",
                "deposit",
                "notes",
                "extensions",
                "appropriated",
                "type",
                "qmname"
            ])

            for row in reader:
                try:
                    user = User.objects.get(old_id=int(row["memberid"]))
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"User not found for old_id {int(row['memberid'])}"))
                    continue

                try:
                    qm_first_name, qm_last_name = row["qmname"].split()
                    qm = User.objects.get(
                        profile__first_name=qm_first_name,
                        profile__last_name=qm_last_name
                    )
                except (User.DoesNotExist, User.MultipleObjectsReturned, ValueError):
                    qm = None

                if row["returndate"] != "NULL":
                    return_date = datetime.strptime(row["returndate"], "%Y-%m-%d").date()
                else:
                    return_date = None

                if row["duedate"] != "0000-00-00":
                    due_date = datetime.strptime(row["duedate"], "%Y-%m-%d").date()
                else:
                    # Seems that old gearmaster allowed empty duedates. There are only about 5 of these, so default to outdate + 1 week
                    due_date = datetime.strptime(row["outdate"], "%Y-%m-%d").date() + timedelta(weeks=1)

                rental, created = Rental.objects.get_or_create(
                    old_id=int(row["id"]),
                    defaults={
                        'type': RentalTypes.GEAR if row["type"] == "0" or row["type"] == "2" else RentalTypes.LIBRARY,
                        'member': user,
                        'what': row["what"],
                        'start_date': datetime.strptime(row["outdate"], "%Y-%m-%d").date(), 
                        'qm': qm,
                        'deposit': parse_deposit(row["deposit"]),
                        'due_date': due_date,
                        'return_date': return_date,
                        'extensions': int(row["extensions"]),
                        'notes': row["notes"] if row["notes"] else None,
                        'lost': row["appropriated"] == "1"
                    }
                )

                if not created:
                    rental.type = RentalTypes.GEAR if row["type"] == "0" or row["type"] == "2" else RentalTypes.LIBRARY
                    rental.member = user
                    rental.what = row["what"]
                    rental.start_date = datetime.strptime(row["outdate"], "%Y-%m-%d").date()
                    rental.qm = qm
                    rental.deposit = parse_deposit(row["deposit"])
                    rental.due_date = due_date
                    rental.return_date = return_date
                    rental.extensions = int(row["extensions"])
                    rental.notes = row["notes"] if row["notes"] else None
                    rental.lost = row["appropriated"] == "1"

                rental.save()

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created rental with old_id {rental.old_id}"))
                else:
                    self.stdout.write(f"Updated rental with old_id {rental.old_id}")

            self.stdout.write(self.style.SUCCESS(f"Gearmaster import completed"))