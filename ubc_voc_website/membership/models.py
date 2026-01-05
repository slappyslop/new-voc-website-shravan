from django.db import models
from django.conf import settings
from django.utils import timezone

from datetime import date
import json

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
    )
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    pronouns = models.CharField(max_length=32, blank=True, null=True)
    phone = models.CharField(max_length=32)
    student_number = models.CharField(max_length=8, blank=True, null=True)
    birthdate = models.DateField(
        default=date(1970, 1, 1)
    )
    bio = models.TextField(blank=True, null=True)
    emergency_info = models.TextField(max_length=512, blank=True, null=True)
    inreach_address = models.TextField(max_length=64, blank=True, null=True)
    acc = models.BooleanField(default=True)
    vocene = models.BooleanField(default=True)
    trip_org_email = models.BooleanField(default=True)
    photo = models.ImageField(upload_to="profile_photos/", blank=True, null=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name_with_pronouns(self):
        if self.pronouns:
            return f"{self.full_name} ({self.pronouns})"
        else:
            return self.full_name
        
    @property
    def bio_html(self):
        if not self.bio:
            return ""
        
        try:
            data = json.loads(self.bio)
            if 'html' in data:
                return data['html']
            elif 'ops' in data:
                return ''.join(f"<p>{op.get('insert','')}</p>" for op in data['ops'])
        except (json.JSONDecodeError, TypeError):
            pass

        return self.bio

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
class Membership(models.Model):
    class MembershipType(models.TextChoices):
        REGULAR = "R"
        ASSOCIATE = "A"
        ACTIVE_HONORARY = "H"
        INACTIVE_HONOURARY = "I"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "start_date"],
                name="unique_membership_user_start"
            )
        ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
    )
    start_date = models.DateField()
    end_date = models.DateField()
    type = models.CharField(
        max_length=1, 
        choices=MembershipType, 
        default=MembershipType.REGULAR
    )
    active = models.BooleanField(default=False)

    def __str__(self):
        return f'{str(self.user)} - {self.type}'
    
    @property
    def type_display_name(self):
        if self.type == Membership.MembershipType.REGULAR:
            return "Regular"
        elif self.type == Membership.MembershipType.ASSOCIATE:
            return "Associate"
        elif self.type == Membership.MembershipType.ACTIVE_HONORARY:
            return "Honorary (Active)"
        else:
            return "Honourary (Inactive)"
    
    @property
    def mapped_status(self):
        if not self.active:
            return "Inactive"
        elif self.end_date >= timezone.localdate():
            return "Active"
        else:
            return "Expired"

class Exec(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
    )
    exec_role = models.CharField(max_length=32)
    priority = models.IntegerField(default=1)

    def __str__(self):
        return f'{self.user} - {self.exec_role}'

class PSG(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        primary_key=True
    )

    def __str__(self):
        return f'{self.user} (PSG)'
    
class Waiver(models.Model):
    membership = models.OneToOneField(
        Membership,
        on_delete=models.CASCADE,
        primary_key=True
    )
    full_name = models.TextField(
        max_length=256
    )
    student_number = models.TextField(
        max_length=8
    )
    guardian_name = models.TextField(
        max_length=256
    )
    signature = models.ImageField(
        upload_to="signatures/"
    )
    paper_waiver = models.BooleanField(
        default=False,
        blank=False
    )
    created = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f'Waiver for {self.full_name} (Membership {self.membership})'
