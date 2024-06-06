from django.db import models
from django.conf import settings

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        primary_key=True
    )
    firstname = models.CharField(max_length=64)
    lastname = models.CharField(max_length=64)
    pronouns = models.CharField(max_length=32)
    phone = models.CharField(max_length=32)
    student_number = models.CharField(max_length=8)
    birthdate = models.DateField()
    blurb = models.TextField()
    acc = models.BooleanField()
    vocene = models.BooleanField()
    trip_org_email = models.BooleanField()

    def __str__(self):
        return self.email
    
class Membership(models.Model):
    class MembershipType(models.TextChoices):
        REGULAR = "R", "Regular"
        ASSOCIATE = "A", "Associate"
        HONORARY = "H", "Honorary"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.PROTECT,
    )
    startdate = models.DateField()
    enddate = models.DateField()
    type = models.CharField(
        max_length=1, 
        choices=MembershipType, 
        default=MembershipType.REGULAR
    )
    active = models.BooleanField()

class Exec(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        primary_key=True
    )
    exec_role = models.CharField(max_length=32)

class PSG(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        primary_key=True
    )

