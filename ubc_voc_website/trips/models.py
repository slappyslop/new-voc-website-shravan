from django.db import models
from django.conf import settings
from django.utils import timezone

from colorfield.fields import ColorField

# helper class, not a model
class TripSignupTypes(models.TextChoices):
    INTERESTED = "interested",
    COMMITTED = "committed",
    GOING = "going"

"""
This is its own model rather than a subclass in the Trip model because it allows any Admin
to add a new tag via the admin centre, rather than required a hardcoded change
"""
class TripTag(models.Model):
    name = models.CharField(max_length=128, blank=False)
    colour = ColorField(default='#808080')

    def __str__(self):
        return self.name
    
class Trip(models.Model):
    class TripStatus(models.TextChoices):
        NO = "N",
        TENTATIVE = "T",
        CANCELLED = "C"

    class SignupStatus(models.TextChoices):
        NOT_ENABLED = "not_enabled",
        NOT_YET_OPEN = "not_yet_open",
        OPEN = "open",
        CLOSED = "closed"

    old_id = models.IntegerField(blank=True, null=True)
    
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
    end_time = models.DateTimeField(blank=True, null=True)
    in_clubroom = models.BooleanField(default=False)
    description = models.TextField(blank=True, null=True)
    use_signup = models.BooleanField(default=False)
    signup_question = models.CharField(max_length=256, blank=True, null=True)
    max_participants = models.IntegerField(blank=True, null=True)
    interested_start = models.DateTimeField(blank=True, null=True)
    interested_end = models.DateTimeField(blank=True, null=True)
    committed_start = models.DateTimeField(blank=True, null=True)
    committed_end = models.DateTimeField(blank=True, null=True)
    use_pretrip = models.BooleanField(default=True)
    pretrip_time = models.DateTimeField(blank=True, null=True)
    pretrip_location = models.CharField(max_length=128, blank=True, null=True)
    drivers_required = models.BooleanField(default=False)

    @property
    def trip_date_as_str_short(self):
        if self.end_time and self.end_time.date() > self.start_time.date():
            return f"{self.start_time.strftime('%a %d')} - {self.end_time.strftime('%a %d')}"
        else:
            return self.start_time.strftime('%a %d')
        
    @property
    def trip_date_as_str_with_year(self):
        if self.end_time and self.end_time.date() > self.start_time.date():
            return f"{self.start_time.strftime('%a %d %b %Y')} - {self.end_time.strftime('%a %d %Y')}"
        else:
            return self.start_time.strftime('%a %d %b %Y')
        
    @property
    def trip_date_as_str_long(self):
        if self.end_time and self.end_time.date() > self.start_time.date():
            return f"{self.start_time.strftime('%A, %B %d')} - {self.end_time.strftime('%A, %B %d')}"
        else:
            return self.start_time.strftime('%A, %B %d')
        
    @property
    def signup_info(self):
        """
        For each signup type, the SignupState, and time until the next state change
        (if signup is open, the time represents how long until it closes. if signup is not open yet, it is how long until it opens)
        """
        signup_info = {
                "interested": (self.SignupStatus.NOT_ENABLED, 0),
                "committed": (self.SignupStatus.NOT_ENABLED, 0)
            }
        if self.use_signup:
            now = timezone.now()
            
            if self.interested_start:
                interested_end = self.interested_end if self.interested_end else self.start_time
                if now < self.interested_start:
                    signup_info["interested"] = (self.SignupStatus.NOT_YET_OPEN.value, self.interested_start)
                elif now < interested_end:
                    signup_info["interested"] = (self.SignupStatus.OPEN.value, interested_end)
                else:
                    signup_info["interested"] = (self.SignupStatus.CLOSED.value, 0)

            if self.committed_start:
                committed_end = self.committed_end if self.committed_end else self.start_time
                if now < self.committed_start:
                    signup_info["committed"] = (self.SignupStatus.NOT_YET_OPEN.value, self.committed_start)
                elif now < committed_end:
                    signup_info["committed"] = (self.SignupStatus.OPEN.value, committed_end)
                else:
                    signup_info["committed"] = (self.SignupStatus.CLOSED.value, 0)
            
        return signup_info
    
    @property
    def valid_signup_types(self):
        """
        A list of the valid signup types for this trip
        based on whether signup is enabled, and signups for interested/committed are open
        """
        signup_types = []
        if self.signup_info["interested"][0] == self.SignupStatus.OPEN:
            signup_types.append(TripSignupTypes.INTERESTED)
        if self.signup_info["committed"][0] == self.SignupStatus.OPEN:
            signup_types.append(TripSignupTypes.COMMITTED)

        return signup_types
    
    def __str__(self):
        return f"{self.name} ({self.trip_date_as_str_with_year})"
        
class TripSignup(models.Model):
    class Meta:
        unique_together = ['user', 'trip']

    trip = models.ForeignKey(
        Trip,
        on_delete=models.CASCADE,
        primary_key=False
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=False
    )
    type = models.CharField(
        max_length=10,
        choices = TripSignupTypes,
        default=TripSignupTypes.INTERESTED
    )
    can_drive = models.BooleanField(default=False)
    car_spots = models.IntegerField(blank=True, null=True)
    signup_answer = models.TextField(max_length=256, blank=True, null=True)

class Meeting(models.Model):
    name = models.CharField(max_length=256)
    start_date = models.DateTimeField()
    end_date = models.DateField()
    duration = models.IntegerField(default=60)
