"""
SELECT ID, post_author, post_date, post_content, post_title, post_name, post_status FROM `wp_posts` where post_type="post" and (post_status="draft" or post_status="pending" or post_status="publish")
"""
from django.core.management import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from tripreports.models import TripReport, TripReportIndexPage

import csv
from datetime import datetime
from wagtail.rich_text import RichText
from zoneinfo import ZoneInfo

pacific_timezone = ZoneInfo("America/Vancouver")

User = get_user_model()

class Command(BaseCommand):
    help="Migrate trip reports from csv"

    def handle(self, *args, **kwargs):
        path = "trip_reports.csv"

        parent = TripReportIndexPage.objects.first()

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=[
                "ID",
                "post_author",
                "post_date",
                "post_content",
                "post_title",
                "post_status"
            ])

            for row in reader:
                try:
                    user = User.objects.get(old_id=row["post_author"])
                except User.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"User not found with old_id {row["post_author"]}"))
                    continue

                if TripReport.objects.filter(old_id=int(row["ID"])).exists():
                    self.stdout.write(f"Skipping trip report with old_id {int(row["ID"])} - already exists")
                    continue

                if not row["post_name"] or not row["post_title"] or not row["post_content"]: # wagtail doesn't permit empty post content, so don't bother migrating these
                    continue

                trip_report = TripReport(
                    title=row["post_title"],
                    slug=slugify(row["post_title"]),
                    body=RichText(row["post_content"]),
                    owner=user,
                    old_id=int(row["ID"]),
                    first_published_at=datetime.strptime(row["post_date"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pacific_timezone)
                )

                parent.add_child(instance=trip_report)
                revision = trip_report.save_revision()

                if row["post_status"] == "publish":
                    revision.publish()
                    self.stdout.write(self.style.SUCCESS(f"Created and published {trip_report.title}"))
                else:
                    trip_report.live = False
                    trip_report.has_unpublished_changes = True
                    trip_report.save()
                    if row["post_status"] == "pending":
                        # Trigger workflow for exec approval
                        workflow = trip_report.get_workflow()
                        if workflow:
                            workflow.start(trip_report, user)
                        self.stdout.write(self.style.SUCCESS(f"Created {trip_report.title} and submitted for approval"))
                    else:
                        self.stdout.write(self.style.SUCCESS(f"Created draft {trip_report.title}"))

            self.stdout.write(self.style.SUCCESS(f"Trip report migration complete"))
