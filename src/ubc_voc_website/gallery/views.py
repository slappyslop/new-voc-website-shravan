import os

from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from django.http import HttpResponseForbidden

from .forms import UserPhotoUploadForm
from .models import UserGallery
from photologue.models import Photo
from ubc_voc_website.decorators import Members

@Members
def manage_user_gallery(request):
    gallery, created = UserGallery.objects.get_or_create(
        user=request.user,
        defaults={
            'title': f"{request.user.get_full_name()}'s Gallery",
            'is_public': True
        }
    )

    if request.method == 'POST':
        form = UserPhotoUploadForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            photo = form.save(commit=False)

            # Update file path to save in a folder for this user
            _, ext = os.path.splitext(form.cleaned_data['image'].name)
            new_path = f"user/{request.user.id}/{slugify(form.cleaned_data['title'].split(':', 1))}{ext}"
            photo.image.name = new_path

            # Update Photo fields
            photo.slug = slugify(photo.title)
            photo.is_public = True
            photo.save()

            gallery.photos.add(photo)

            return redirect('manage_user_gallery')

    else:
        form = UserPhotoUploadForm(user=request.user)

    return render(request, 'gallery/user_gallery.html', {
        'gallery': gallery,
        'form': form
    })

@Members
def delete_user_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if not photo.public_galleries().filter(id=request.user.gallery.id).exists():
        return HttpResponseForbidden("You don't have permission to delete this photo")
    
    photo.delete()
    return redirect('manage_user_gallery')

@Members
def create_trip_gallery(request):
    pass

@Members
def add_trip_gallery_photo(request):
    pass
