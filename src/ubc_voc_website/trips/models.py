from django.db import models
from django.conf import settings
from django.utils import timezone

from colorfield.fields import ColorField

# helper class, not a model
class TripSignupTypes(models.TextChoices):
    INTERESTED = "I",
    COMMITTED = "C",
    GOING = "G"

"""
This is its own model rather than a subclass in the Trip model because it allows any Admin
to add a new tag via the admin centre, rather than required a hardcoded change
"""
class TripTag(models.Model):
    name = models.CharField(max_length=32, blank=False)
    colour = ColorField(default='#808080')

    def __str__(self):
        return self.name
    
class Trip(models.Model):
    class TripStatus(models.TextChoices):
        NO = "N",
        TENTATIVE = "T",
        CANCELLED = "C"

    name = models.CharField(max_length=256, blank=False)
    organizers = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="organized_trips",
        blank=False
    )
    published = models.BooleanField(default=False)
    status = models.CharField(
        max_length=1,
        choices=TripStatus,
        default=TripStatus.NO
    )
    tags = models.ManyToManyField(
        TripTag,
        related_name="tagged_trips",
        blank=True
    )
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True)
    description = models.TextField(null=True)
    use_signup = models.BooleanField(default=False)
    signup_question = models.CharField(max_length=256, null=True)
    max_participants = models.IntegerField(null=True)
    interested_start = models.DateTimeField(null=True)
    interested_end = models.DateTimeField(null=True)
    committed_start = models.DateTimeField(null=True)
    committed_end = models.DateTimeField(null=True)
    use_pretrip = models.BooleanField(default=False)
    pretrip_time = models.DateTimeField(null=True)
    pretrip_location = models.CharField(max_length=128)
    drivers_required = models.BooleanField(default=False)

    @property
    def trip_date_as_str_short(self):
        if self.end_time and self.end_time.date() > self.start_time.date():
            return f"{self.start_time.strftime('%a %d')} - {self.end_time.strftime('%a %d')}"
        else:
            return self.start_time.strftime('%a %d')
        
    @property
    def trip_date_as_str_long(self):
        if self.end_time and self.end_time.date() > self.start_time.date():
            return f"{self.start_time.strftime('%A, %B %d')} - {self.end_time.strftime('%A, %B %d')}"
        else:
            return self.start_time.strftime('%A, %B %d')
        
    @property
    def valid_signup_types(self):
        """
        A list of the valid signup types for this trip
        based on whether signup is enabled, and signups for interested/committed are open
        """
        signup_types = []
        if self.use_signup:
            now = timezone.now()
            if self.interested_start <= now and self.interested_end >= now:
                signup_types.append(TripSignupTypes.INTERESTED)
            if self.committed_start <= now and self.committed_end >= now:
                signup_types.append(TripSignupTypes.COMMITTED)
        return signup_types
        
class TripSignup(models.Model):
    trip = models.OneToOneField(
        Trip,
        on_delete=models.CASCADE,
        primary_key=False
    )
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=False
    )
    type = models.CharField(
        max_length=1,
        choices = TripSignupTypes,
        default=TripSignupTypes.INTERESTED
    )
    can_drive = models.BooleanField(default=False)
    signup_answer = models.TextField(max_length=256, null=True)
