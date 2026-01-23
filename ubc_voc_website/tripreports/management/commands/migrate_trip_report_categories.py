"""
SELECT 
    p.ID as post_id, 
    t.name as category_name, 
    t.slug as category_slug
FROM 
    wp_posts p
INNER JOIN 
    wp_term_relationships rel ON p.ID = rel.object_id
INNER JOIN 
    wp_term_taxonomy tax ON rel.term_taxonomy_id = tax.term_taxonomy_id
INNER JOIN 
    wp_terms t ON tax.term_id = t.term_id
WHERE 
    p.post_type = 'post' 
    AND p.post_status = 'publish'
    AND tax.taxonomy = 'category';
"""
from django.core.management import BaseCommand

from tripreports.models import TripReport, TripReportCategory

import csv

class Command(BaseCommand):
    help="Migrate trip report categories from csv"

    def handle(self, *args, **kwargs):
        path = "trip_report_categories.csv"

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=[
                "post_id",
                "category_name",
                "category_slug"
            ])

            for row in reader:
                try:
                    trip_report = TripReport.objects.get(old_id=int(row["post_id"]))
                except TripReport.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Trip report does not exist with old_id {int(row["post_id"])}"))
                    continue

                try:
                    category = TripReportCategory.get(name=row["category_name"])
                except TripReportCategory.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Trip report category {row["category_name"]} does not exist"))
                    continue

                trip_report.categories.add(category)
                self.stdout.write(self.style.SUCCESS(f"Added category {row["category_name"]} to trip report with old_id {int(row["post_id"])}"))

            self.stdout.write(self.style.SUCCESS("Trip report category migration complete"))

