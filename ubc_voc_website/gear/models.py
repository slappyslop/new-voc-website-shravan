from django.db import models
from django.conf import settings
from django.utils import timezone

import datetime

class RentalTypes(models.IntegerChoices):
    GEAR = 1,
    LIBRARY = 2

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
    start_date = models.DateField()
    end_date = models.DateField()
    start_time = models.TimeField(default=datetime.time(0, 0))
    duration = models.IntegerField()

class CancelledGearHour(models.Model):
    gear_hour = models.ForeignKey(
        GearHour,
        on_delete=models.CASCADE,
        related_name="cancelled_dates"
    )
    date = models.DateField()

class Rental(models.Model):
    class RentalStatus(models.TextChoices):
        RETURNED_ON_TIME = "returned_on_time"
        RETURNED_LATE = "returned_late"
        OUT_ON_TIME = "out_on_time"
        OUT_LATE = "out_late"
        LOST = "lost"

    old_id = models.IntegerField(blank=True, null=True)

    type = models.IntegerField(
        choices=RentalTypes,
        default=RentalTypes.GEAR
    )

    qm = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete = models.PROTECT,
        related_name="+",
        blank=True,
        null=True
    )
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+"
    )
    deposit = models.IntegerField()
    start_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    extensions = models.IntegerField(default=0)
    what = models.TextField()
    notes = models.TextField(blank=True, null=True)
    lost = models.BooleanField(default=False)

    @property
    def status(self):
        if self.return_date:
            if self.return_date > self.due_date:
                return Rental.RentalStatus.RETURNED_LATE
            else:
                return Rental.RentalStatus.RETURNED_ON_TIME
        elif self.lost:
            return Rental.RentalStatus.LOST
        elif self.due_date < timezone.localdate():
            return Rental.RentalStatus.OUT_LATE
        else:
            return Rental.RentalStatus.OUT_ON_TIME
