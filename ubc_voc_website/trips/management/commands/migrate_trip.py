from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from trips.models import Trip

import csv
from datetime import datetime

User = get_user_model()

class Command(BaseCommand):
    help="Migrate Trips from CSV"

    def handle(self, *args, **kwargs):
        path = "trips.csv"

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=[
                "id",
                "name", 
                "organizerid", 
                "tentative", 
                "cancelled", 
                "starttime", 
                "endtime", 
                "blurb", 
                "usesignup", 
                "questions",
                "maxparticipants",
                "interestedstart",
                "interestedend",
                "committedstart",
                "committedend",
                "pretriptime",
                "pretriploc",
                "needtodrive"
            ])

            for row in reader:
                try:
                    user = User.objects.get(old_id=int(row["organizerid"]))
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"User not found for old_id {int(row["organizerid"])}"))
                    continue

                if row['tentative'] == "1":
                    status = Trip.TripStatus.TENTATIVE
                if row['cancelled'] == "1":
                    status = Trip.TripStatus.CANCELLED
                else:
                    status = Trip.TripStatus.NO

                if row['endtime'] == "0000-00-00 00:00:00":
                    end_time = None
                else:
                    end_time = timezone.make_aware(datetime.strptime(row['endtime'], "%Y-%m-%d %H:%M:%S"))

                trip, created = Trip.objects.get_or_create(
                    old_id=int(row['id']),
                    defaults={
                        'name': row['name'],
                        'start_time': timezone.make_aware(datetime.strptime(row['starttime'], "%Y-%m-%d %H:%M:%S")),
                    }
                    
                )

                trip.name = row['name']

                if created:
                    trip.organizers.add(user)

                trip.published = True
                trip.status = status
                trip.start_time = timezone.make_aware(datetime.strptime(row['starttime'], "%Y-%m-%d %H:%M:%S"))
                trip.end_time = end_time
                trip.in_clubroom = False
                trip.description = row['blurb']
                trip.use_signup = row['usesignup'] == 1

                if trip.use_signup:
                    trip.signup_question = row['questions']
                    trip.max_participants = int(row['maxparticipants'])
                    trip.interested_start = timezone.make_aware(datetime.strptime(row['interestedstart'], "%Y-%m-%d %H:%M:%S"))
                    trip.interested_end = timezone.make_aware(datetime.strptime(row['interestedend'], "%Y-%m-%d %H:%M:%S"))
                    trip.committed_start = timezone.make_aware(datetime.strptime(row['committedstart'], "%Y-%m-%d %H:%M:%S"))
                    trip.committed_end = timezone.make_aware(datetime.strptime(row['committedend'], "%Y-%m-%d %H:%M:%S"))

                trip.use_pretrip = row['pretriptime'] != "0000-00-00 00:00:00"
                if trip.use_pretrip:
                    trip.pretrip_time = timezone.make_aware(datetime.strptime(row['pretriptime'], "%Y-%m-%d %H:%M:%S"))
                    trip.pretrip_location = row['pretriploc']

                trip.drivers_required = row['needtodrive'] == "1"

                trip.save()

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created trip with old_id {int(row['id'])}"))
                else:
                    self.stdout.write(f"Updated trip with old_id {int(row['id'])}")

            self.stdout.write(self.style.SUCCESS(f"Trip migration complete"))