from django.db import models
from django.conf import settings

import datetime

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        primary_key=True
    )
    first_name = models.CharField(max_length=64, blank=False)
    last_name = models.CharField(max_length=64, blank=False)
    pronouns = models.CharField(max_length=32, null=True)
    phone = models.CharField(max_length=32, blank=False)
    student_number = models.CharField(max_length=8, null=True)
    birthdate = models.DateField(
        null=False,
        default=datetime.date.today
    )
    blurb = models.TextField(null=True)
    acc = models.BooleanField(default=True)
    vocene = models.BooleanField(default=True)
    trip_org_email = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
    
class Membership(models.Model):
    class MembershipType(models.TextChoices):
        REGULAR = "R", "Regular"
        ASSOCIATE = "A", "Associate"
        HONORARY = "H", "Honorary"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
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

class Exec(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        primary_key=True
    )
    exec_role = models.CharField(max_length=32)

    def __str__(self):
        return f'{self.user} - {self.exec_role}'

class PSG(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        primary_key=True
    )

    def __str__(self):
        return f'{self.user} (PSG)'
    
class Waiver(models.Model):
    membership = models.OneToOneField(
        Membership,
        on_delete=models.PROTECT,
        primary_key=True
    )
    full_name = models.TextField(
        max_length=256,
        blank=False
    )
    student_number = models.TextField(
        max_length=8
    )
    guardian_name = models.TextField(
        max_length=256
    )
    signature = models.ImageField(
        upload_to="signatures/",
        blank=False
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
