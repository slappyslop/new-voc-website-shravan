import os

from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from .forms import TripPhotoUploadForm, UserPhotoUploadForm
from .models import TripGallery, UserGallery
from trips.models import Trip, TripSignup, TripSignupTypes
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

    return render(request, 'gallery/gallery.html', {
        'gallery': gallery,
        'form': form
    })

@Members
def delete_user_photo(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    if not photo.public_galleries().filter(id=request.user.gallery.id).exists():
        return render(request, 'access_denied.html', status=403)
    
    photo.delete()
    return redirect('manage_user_gallery')

@Members
def manage_trip_gallery(request, trip_id):
    trip = get_object_or_404(Trip, id=trip_id)

    going_list = TripSignup.objects.filter(trip=trip, type=TripSignupTypes.GOING)
    if not going_list.filter(user=request.user).exists():
        return render(request, 'access_denied.html', status=403)
    
    gallery_name = f"Trip Gallery: {trip.name}"
    gallery, created = TripGallery.objects.get_or_create(
        trip=trip,
        defaults={
            'title': gallery_name,
            'slug': slugify(gallery_name),
            'is_public': True
        }
    )

    if request.method == 'POST':
        form = TripPhotoUploadForm(request.POST, request.FILES, trip=trip)
        if form.is_valid():
            photo = form.save(commit=False)

            # Update file path to save in folder for this trip
            _, ext = os.path.splitext(form.cleaned_data['image'].name)
            new_path = f"trip/{trip_id}/{slugify(form.cleaned_data['title'].split(':', 1))}{ext}"
            photo.image.name = new_path

            # Update Photo Fields
            photo.slug = slugify(photo.title)
            photo.is_public = True
            photo.save()

            gallery.photos.add(photo)

            return redirect('manage_trip_gallery', trip_id=trip_id)
        
    else:
        form = TripPhotoUploadForm(trip=trip)

    return render(request, 'gallery/gallery.html', {
        'gallery': gallery,
        'form': form
    })
