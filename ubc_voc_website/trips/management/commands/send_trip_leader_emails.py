from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.management import BaseCommand
from django.template.loader import render_to_string
from django.utils import timezone

from trips.models import Trip

class Command(BaseCommand):
    help = "Send trip leader email to organizers whose trips are a week away"

    def handle(self, *args, **kwargs):
        today = timezone.localdate()
        target_trip_date = today + timezone.timedelta(days=7)

        trips = Trip.objects.filter(
            start_time__date=target_trip_date, published=True
        ).exclude(
            status=Trip.TripStatus.CANCELLED
        ).prefetch_related("organizers")

        if not trips.exists():
            self.stdout.write("No trips starting in 7 days")
            return
        
        for trip in trips:
            for organizer in trip.organizers.all():
                if getattr(organizer, "profile").trip_org_email:
                    context = {
                        "name": organizer.get_full_name(),
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
