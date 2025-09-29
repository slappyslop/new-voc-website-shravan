from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import CustomUserCreationForm

import random
from photologue.models import Gallery

PHOTO_CONTEST_ALBUM = "photo-contest-2025"

def home(request):
    try:
        photo_contest_gallery = Gallery.objects.get(slug=PHOTO_CONTEST_ALBUM)
        photos = list(photo_contest_gallery.photos.all())
        photo = random.choice(photos) if photos else None
    except Gallery.DoesNotExist:
        photo = None

    return render(request, 'home.html', {'photo': photo})

def join(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('join')
        else:
            print(form.errors)
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/join.html', {'form': form})