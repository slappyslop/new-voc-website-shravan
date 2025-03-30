from django.db import models
from django.conf import settings


class GearHour(models.Model):
    qm = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    """
    Since gear hours are often recurring at the same day/time each week, this is set up as a recurring event
    This way QMs can post their hours once per semester (or whenever they change), and they won't have to update them weekly

    The downside to this approach is it requires a second model for CancelledGearHours, because there needs to be a way
    to cancel a gear hour for one week without deleting the whole recurrence
    """
    start_date = models.DateTimeField()
    end_date = models.DateField()
    duration = models.IntegerField(default=60)

class CancelledGearHour(models.Model):
    gear_hour = models.ForeignKey(
        GearHour,
        on_delete=models.CASCADE,
        related_name="cancelled_dates"
    )
    date = models.DateTimeField()
