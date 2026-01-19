from django.shortcuts import render

from photologue.models import Gallery

PHOTO_CONTEST_ALBUM = "photo-contest-2025"

def home(request):
    gallery = Gallery.objects.filter(slug="homepage").first()
    photos = gallery.public() if gallery else []
    return render(request, "home.html", {"photos": photos})

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")