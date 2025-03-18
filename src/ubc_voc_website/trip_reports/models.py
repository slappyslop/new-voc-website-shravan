from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation

from trips.models import Trip
from comment.models import Comment

class TripReportStatus(models.TextChoices):
        DRAFT = "D",
        PUBLISHED = "P"

class TripReportPrivacyStatus(models.TextChoices):
    PRIVATE = "PR"
    PUBLIC = "PU"

class TripReport(models.Model):
    trip = models.OneToOneField(
        Trip,
        on_delete=models.PROTECT
    )
    title = models.CharField(max_length=256, blank=False)
    authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="written_trip_reports",
        blank=False
    )
    status = models.CharField(
        max_length=1,
        choices=TripReportStatus,
        default=TripReportStatus.DRAFT
    )
    privacy = models.CharField(
        max_length=2,
        choices=TripReportPrivacyStatus,
        default=TripReportPrivacyStatus.PRIVATE
    )
    content = models.TextField(null=False)
    comments = GenericRelation(Comment)

