from django.db import models
from django.conf import settings

from photologue.models import Gallery
from trips.models import Trip

class TripGallery(Gallery):
    trip = models.OneToOneField(
        Trip,
        on_delete=models.CASCADE,
        related_name="gallery"
    )

class UserGallery(Gallery):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="gallery"
    )
