"""
SELECT membership_id, fullname, guardian_name, studentnumber, signature, paper_waiver, saved FROM `member_waivers`
"""

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from membership.models import Membership, Waiver

import base64
from cairosvg import svg2png
import csv
from datetime import datetime
import re
import uuid
from zoneinfo import ZoneInfo

pacific_timezone = ZoneInfo("America/Vancouver")

class Command(BaseCommand):
    help="Migrate waivers from CSV"

    def handle(self, *args, **kwargs):
        path = "waivers.csv"

        def safe_b64decode(data):
            data = re.sub(r'^data:image\/[^;]+;base64,', '', data)
            data = re.sub(r'\s+', '', data)

            missing_padding = len(data) % 4
            if missing_padding:
                data += '=' * (4 - missing_padding)
            return base64.b64decode(data)
        

        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f, fieldnames=[
                "membership_id",
                "fullname",
                "guardian_name",
                "studentnumber",
                "signature",
                "paper_waiver",
                "saved"
            ])

            for row in reader:
                try:
                    membership = Membership.objects.get(id=int(row["membership_id"]))
                except Membership.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Membership not found with old_id {int(row['membership_id'])}"))

                if not row["signature"]:
                    self.stdout.write(self.style.WARNING(f"Skipping waiver for membership with old_id {int(row['membership_id'])} - signature is empty"))
                    continue

                signature_svg_data = row["signature"].split(",", 1)[1]
                siganture_svg_bytes = safe_b64decode(signature_svg_data)
                signature_png_bytes = svg2png(bytestring=siganture_svg_bytes)
                signature_filename = f"signature_{uuid.uuid4().hex}.png"
                signature = ContentFile(signature_png_bytes, signature_filename)
                
                waiver, created = Waiver.objects.get_or_create(
                    membership=membership
                )

                waiver.full_name = row["fullname"]
                waiver.student_number = row["studentnumber"],
                waiver.guardian_name = row["guardian_name"]
                waiver.signature = signature
                waiver.paper_waiver = row["paper_waiver"] == "1"
                waiver.created = datetime.strptime(row["saved"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=pacific_timezone)

                if created:
                    self.stdout.write(self.style.SUCCESS(f"Created waiver for membership with old_id {int(row['membership_id'])}"))
                else:
                    self.stdout.write(f"Waiver already exists for membership with old_id {{int(row['membership_id'])}}")

            self.stdout.write(self.style.SUCCESS(f"Waiver migration complete"))