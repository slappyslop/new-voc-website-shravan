from django.shortcuts import render
from django.http import HttpResponseRedirect

from django.views.decorators.http import require_POST

from .models import UserGallery
from ubc_voc_website.decorators import Admin, Members, Execs

@Members
@require_POST
def create_user_gallery(request):
    gallery, created = UserGallery.objects.get_or_create(
        user=request.user,
        defaults={
            'title': f"{request.user.get_full_name()}'s Gallery",
            'is_public': True
        }
    )
    return HttpResponseRedirect(request.path_info)

@Members
def manage_trip_gallery(request):
    pass
