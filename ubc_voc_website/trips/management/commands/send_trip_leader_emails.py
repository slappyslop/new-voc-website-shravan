from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management import BaseCommand
from django.template.loader import render_to_string

from django.utils import timezone

from trips.models import Trip

import datetime
from zoneinfo import ZoneInfo

pacific_timezone = ZoneInfo("America/Vancouver")

class Command(BaseCommand):
    help = "Send trip leader email to organizers whose trips are a week away"

    def handle(self, *args, **kwargs):
        pacific_now = timezone.localtime(timezone.now(), pacific_timezone)
        target_trip_date = (pacific_now + datetime.timedelta(days=7)).date()

        pacific_start = datetime.datetime.combine(target_trip_date, datetime.time.min, tzinfo=pacific_timezone)
        pacific_end = datetime.datetime.combine(target_trip_date, datetime.time.max, tzinfo=pacific_timezone)

        start_utc = pacific_start.astimezone(datetime.timezone.utc)
        end_utc = pacific_end.astimezone(datetime.timezone.utc)

        # debug output, remove when done
        self.stdout.write(f"Computed Pacific target date: {target_trip_date} -> UTC range: {start_utc} to {end_utc}")

        trips = Trip.objects.filter(
            start_time__gte=start_utc,
            start_time__lte=end_utc,
            published=True
        ).exclude(
            status=Trip.TripStatus.CANCELLED
        ).prefetch_related("organizers")

        if not trips.exists():
            self.stdout.write("No trips starting in 7 days")
            return
        
        for trip in trips:
            for organizer in trip.organizers.all():
                profile = getattr(organizer, "profile")
                if profile.trip_org_email:
                    context = {
                        "name": profile.full_name,
                        "site_url": settings.SITE_URL
                    }

                    text_body = render_to_string(
                        "trips/emails/trip_leader_email.txt",
                        context
                    )
                    html_body = render_to_string(
                        "trips/emails/trip_leader_email.html",
                        context
                    )

                    message = EmailMultiAlternatives(
                        subject=f"VOC Trip Leader Email",
                        body=text_body,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to=[organizer.email]
                    )
                    message.attach_alternative(html_body, "text/html")
                    message.send()

                    self.stdout.write(self.style.SUCCESS(f"Sent Trip Leader email to {organizer.email} for trip {trip.name}"))
        
        self.stdout.write(self.style.SUCCESS("Trip leader emails complete"))
