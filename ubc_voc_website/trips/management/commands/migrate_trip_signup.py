"""
select memberid, tripid, signupclass, signuptime, driving, answers from participation
"""

from django.core.management import BaseCommand
from django.contrib.auth import get_user_model

from trips.models import Trip, TripSignup, TripSignupTypes

import csv
from datetime import datetime
from zoneinfo import ZoneInfo

pacific_timezone = ZoneInfo("America/Vancouver")

User = get_user_model()

class Command(BaseCommand):
    help="Migrate TripSignup from CSV"

    def handle(self, *args, **kwargs):
        path="trip_signups.csv"

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=[
                "memberid", 
                "tripid", 
                "signupclass", 
                "signuptime", 
                "driving", 
                "answers", 
            ])

            for row in reader:
                try:
                    user = User.objects.get(old_id=int(row["memberid"]))
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"User not found for old_id {int(row["memberid"])}"))
                    continue

                try:
                    trip = Trip.objects.get(old_id=int(row["tripid"]))
                except Trip.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Trip not found for old_id {int(row["tripid"])}"))

                match int(row["signupclass"]):
                    case -3:
                        type = TripSignupTypes.NO_LONGER_GOING
                    case -2:
                        type = TripSignupTypes.BAILED_FROM_COMMITTED
                    case -1:
                        type = TripSignupTypes.NO_LONGER_INTERESTED
                    case 0: # This was for the "off-list" feature on the old site and hasn't been used since 2011
                        continue
                    case 1:
                        type = TripSignupTypes.INTERESTED
                    case 2:
                        type = TripSignupTypes.COMMITTED
                    case 3:
                        type = TripSignupTypes.GOING

                signup, created = TripSignup.objects.get_or_create(
                    user=user,
                    trip=trip
                )

                signup.type = type
                if int(row["driving"]) > 0:
                    signup.can_drive = True
                    signup.car_spots = int(row["driving"])
                
                signup.signup_answer = row["answers"]
                signup.signup_time = datetime.strptime(row['signuptime'], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pacific_timezone)

                signup.save()

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created signup for user {int(row["memberid"])} for trip {int(row["tripid"])}"))
                else:
                    self.stdout.write(f"Updated signup for user {int(row["memberid"])} for trip {int(row["tripid"])}")

            self.stdout.write(self.style.SUCCESS(f"Trip signup migration complete"))
