"""
SELECT p.ID, u.user_email, p.post_date, p.post_title 
FROM `wp_posts` as p inner join `wp_users` as u on p.post_author = u.ID 
where post_type="post" and post_status="publish"
"""
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management import BaseCommand
from django.utils.text import slugify

from tripreports.models import TripReport, TripReportIndexPage

import csv
from datetime import datetime
import os
from wagtail.documents.models import Document
from wagtail.rich_text import RichText
from zoneinfo import ZoneInfo

pacific_timezone = ZoneInfo("America/Vancouver")

User = get_user_model()

class Command(BaseCommand):
    help="Migrate published tirp report metadata from csv, and attach pdf content"

    def handle(self, *args, **kwargs):
        path = "trip_reports_published.csv"
        pdf_dir = "trip_report_pdfs/"
        pdf_files = os.listdir(pdf_dir)

        parent = TripReportIndexPage.objects.first()

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=[
                "ID",
                "post_author_email",
                "post_date",
                "post_title",
            ])

            orphaned_emails = []

            for row in reader:
                try:
                    user = User.objects.get(email=row["post_author_email"])
                except User.DoesNotExist:
                    orphaned_emails.append(row["post_author_email"])
                    self.stdout.write(self.style.warning(f"User not found with email {row['post_author_email']}"))
                    continue

                if TripReport.objects.filter(old_id=int(row["ID"])).exists():
                    self.stdout.write(f"Skipping '{row["post_title"]}' - report already exists")
                    continue

                pdf = None
                try:
                    pdf_filename = next((p for p in pdf_files if p.startswith(f"{int(row['ID'])}_")), None)
                    if pdf_filename:
                        pdf_filepath = os.path.join(pdf_dir, pdf_filename)
                        with open(pdf_filepath, 'rb') as pdf_file:
                            pdf = Document(
                                title=row["post_title"],
                                file=File(pdf_file, name=pdf_filename)
                            )
                            pdf.save()
                            self.stdout.write(self.style.SUCCESS(f"Attached pdf file for '{row["post_title"]}'"))
                    else:
                        self.stdout.write(self.style.ERROR(f"No pdf found for '{row["post_title"]}'"))
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error processing pdf for '{row["post_title"]}': {e}"))

                try:
                    trip_report = TripReport(
                        title=row["post_title"],
                        slug=slugify(row["post_title"]-row["ID"]),
                        body=RichText(""),
                        owner=user,
                        old_id=int(row["ID"]),
                        first_published_at=datetime.strptime(row["post_date"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pacific_timezone),
                        legacy_pdf=pdf
                    )

                    parent.add_child(trip_report)
                    trip_report.save_revision().publish()

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Failed to create trip report for '{row["post_title"]}'"))

            self.stdout.write(self.style.SUCCESS(f"Published trip report migration complete"))
            