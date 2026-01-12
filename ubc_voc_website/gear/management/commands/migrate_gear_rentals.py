"""
SELECT memberid, outdate, duedate, returndate, what, deposit, notes, extensions, appropriated, type, qmname FROM `gear`
"""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from gear.models import BookRental, GearRental

import csv
from datetime import datetime
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

                qm = None
                if row["qmname"] and row["qmname"] != "NULL":
                    qm_first_name, qm_last_name = row["qmname"].split()
                    qm = User.objects.get(
                        profile__first_name=qm_first_name,
                        profile__last_name=qm_last_name
                    )

                if row["type"] == "0" or row["type"] == "2": # Gear
                    rental, created = GearRental.objects.get_or_create(
                        member=user,
                        what=row["what"],
                        defaults={
                            'qm': qm,
                            'deposit': parse_deposit(row["deposit"]),
                            'start_date': datetime.strptime(row["outdate"], "%Y-%m-%d").date(),
                            'due_date': datetime.strptime(row["duedate"], "%Y-%m-%d").date(),
                            'return_date': datetime.strptime(row["returndate"], "%Y-%m-%d").date(),
                            'extensions': int(row["extensions"]),
                            'notes': row["notes"] if row["notes"] else None,
                            'lost': row["appropriated"] == "1"
                        }
                    )

                    if not created:
                        rental.qm = qm
                        rental.deposit = parse_deposit(row["deposit"])
                        rental.start_date = datetime.strptime(row["outdate"], "%Y-%m-%d").date()
                        rental.due_date = datetime.strptime(row["duedate"], "%Y-%m-%d").date()
                        rental.return_date = datetime.strptime(row["returndate"], "%Y-%m-%d").date()
                        rental.extensions = int(row["extensions"])
                        rental.notes = row["notes"] if row["notes"] else None
                        rental.lost = row["appropriated"] == "1"

                    rental.save()
                    self.stdout.write(self.style.SUCCESS(f"Created gear rental for user with old_id {user.old_id}"))

                else: #Library
                    rental, created = BookRental.objects.get_or_create(
                        member=user,
                        what=row["what"],
                        default={
                            'qm': qm,
                            'deposit': parse_deposit(row["deposit"]),
                            'start_date': datetime.strptime(row["outdate"], "%Y-%m-%d").date(),
                            'due_date': datetime.strptime(row["duedate"], "%Y-%m-%d").date(),
                            'return_date': datetime.strptime(row["returndate"], "%Y-%m-%d").date(),
                            'extensions': int(row["extensions"]),
                            'notes': row["notes"] if row["notes"] else None,
                            'lost': row["appropriated"] == "1"
                        }
                    )

                    if not created:
                        rental.qm = qm
                        rental.deposit = parse_deposit(row["deposit"])
                        rental.start_date = datetime.strptime(row["outdate"], "%Y-%m-%d").date()
                        rental.due_date = datetime.strptime(row["duedate"], "%Y-%m-%d").date()
                        rental.return_date = datetime.strptime(row["returndate"], "%Y-%m-%d").date()
                        rental.extensions = int(row["extensions"])
                        rental.notes = row["notes"] if row["notes"] else None
                        rental.lost = row["appropriated"] == "1"

                    rental.save()
                    self.stdout.write(self.style.SUCCESS(f"Created book rental for user with old_id {user.old_id}"))

            self.stdout.write(self.style.SUCCESS(f"Gearmaster import completed"))