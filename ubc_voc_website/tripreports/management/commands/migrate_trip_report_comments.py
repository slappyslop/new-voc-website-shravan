"""

"""
from django.contrib.auth import get_user_model
from django.core.management import BaseCommand

from tripreports.models import Comment, TripReport

import csv
from datetime import datetime
from zoneinfo import ZoneInfo

pacific_timezone = ZoneInfo("America/Vancouver")

User = get_user_model()

class Command(BaseCommand):
    help="Migrate trip report comments from csv"

    def handle(self, *args, **kwargs):
        path = "trip_report_comments.csv"

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=[
                "comment_post_ID",
                "comment_author_email",
                "comment_date",
                "comment_content"
            ])

            orphaned_emails = set()
            missing_trip_reports = set()

            for row in reader:
                try:
                    user = User.objects.get(email=row["comment_author_email"])
                except User.DoesNotExist:
                    orphaned_emails.add(row["comment_author_email"])
                    self.stdout.write(self.style.WARNING(f"User not found with email {row["comment_author_email"]}"))
                    continue

                try:
                    trip_report = TripReport.objects.get(old_id=int(row["comment_post_ID"]))
                except TripReport.DoesNotExist:
                    missing_trip_reports.add(int(row["comment_post_ID"]))
                    self.stdout.write(self.style.WARNING(f"Trip report with old_id {int(row["comment_post_ID"])} does not exist"))
                    continue

                comment, created = Comment.objects.get_or_create(
                    trip_report=trip_report,
                    user=user,
                    timestamp=datetime.strptime(row["comment_date"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pacific_timezone),
                    defaults={
                        "content": row["comment_content"]
                    }
                )

                if created:
                    comment.save()
                    self.stdout.write(self.style.SUCCESS(f"Created comment from {user.display_name} on trip report with old_id {int(row["comment_post_ID"])}"))
                else:
                    self.stdout.write(f"Comment from {user.display_name} on post with old_id {int(row["comment_post_ID"])} already exists")
            
            self.stdout.write(self.style.SUCCESS("Trip report comment migration complete"))
            self.stdout.write(self.style.WARNING(f"Orphaned emails: {orphaned_emails}"))
            self.stdout.write(self.style.WARNING(f"Missing trip reports: {missing_trip_reports}"))
