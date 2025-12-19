from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import CustomUserCreationForm

import jwt
import random
import time
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

@login_required
def wordpress_sso(request):
    user = request.user

    payload = {
        "iss": "django",
        "iat": int(time.time()),
        "exp": int(time.time()) + 300,
        "sub": str(user.id),
        "email": user.email,
        "name": user.profile.full_name(),
        "roles": ["author"],
    }

    token = jwt.encode(
        payload,
        settings.WP_SSO_SECRET,
        algorithm="HS256"
    )

    return redirect(
        f"{settings.WP_SSO_URL}?sso={token}"
    )