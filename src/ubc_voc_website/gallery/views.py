from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponseRedirect
from django.utils.text import slugify

from django.views.decorators.http import require_POST

from .models import UserGallery
from .forms import PhotoUploadForm
from ubc_voc_website.decorators import Admin, Members, Execs

@Members
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
def manage_user_gallery(request):
    gallery = get_object_or_404(UserGallery, user=request.user)

    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            photo = form.save(commit=False)

            photo.title = form.cleaned_data['title']
            photo.caption = f"Photo: {request.user.get_full_name()}"
            photo.slug = slugify(photo.title)
            photo.is_public = True
            photo.save()

            gallery.photos.add(photo)

    else:
        form = PhotoUploadForm()

    return render(request, 'gallery/user_gallery.html', {
        'gallery': gallery,
        'form': form
    })

@Members
def create_trip_gallery(request):
    pass

@Members
def add_trip_gallery_photo(request):
    pass
