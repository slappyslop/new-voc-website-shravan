from django.core.files.storage import default_storage
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from .decorators import Members
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

@csrf_exempt
@Members
def quill_image_upload(request):
    if request.method == "POST" and request.FILES.get("image"):
        image_file = request.FILES["image"]
        path = default_storage.save(f"uploads/quill/{image_file.name}", image_file)
        url = default_storage.url(path)
        return JsonResponse({"url": url})
    return JsonResponse({"error": "Failed to upload image"}, status=403)