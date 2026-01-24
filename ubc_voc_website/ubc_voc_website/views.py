from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .decorators import Members
from photologue.models import Gallery, Photo

PHOTO_CONTEST_ALBUM = "photo-contest-2025"

def home(request):
    gallery = Gallery.objects.filter(slug="homepage").first()
    gallery_photos = gallery.public() if gallery else []

    about_photo = Photo.objects.get(slug="about")
    join_photo = Photo.objects.get(slug="join")
    trips_photo = Photo.objects.get(slug="trips")
    huts_photo = Photo.objects.get(slug="huts")

    return render(request, "home.html", {
        "photos": gallery_photos,
        "about": about_photo,
        "join": join_photo,
        "trips": trips_photo,
        "huts": huts_photo
    })

def about(request):
    return render(request, "about.html")

def contact(request):
    return render(request, "contact.html")

@csrf_exempt
@Members
def quill_image_upload(request):
    if request.method == "POST" and request.FILES.get("image"):
        image_file = request.FILES["image"]
        path = default_storage.save(f"uploads/quill/{image_file.name}", image_file)
        url = default_storage.url(path)
        return JsonResponse({"url": url})
    return JsonResponse({"error": "Failed to upload image"}, status=403)