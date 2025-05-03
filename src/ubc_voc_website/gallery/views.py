from django.shortcuts import render

from django.contrib.auth.decorators import login_required

from .models import UserGallery
from ubc_voc_website.decorators import Admin, Members, Execs

@Members
def manage_user_gallery(request):
    gallery, created = UserGallery.objects.get_or_create(
        user=request.user,
        default={
            'title': f"{request.user.get_full_name()}'s Gallery",
            'is_public': True
        }
    )

@Members
def manage_trip_gallery(request):
    pass
