from django.core.files import File
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from membership.models import Profile

import os

User = get_user_model()

class Command(BaseCommand):
    help="Migrate profile photos from a folder"

    def handle(self, *args, **kwargs):
        path="profile_pics"
        for filename in os.listdir(path):
            if not filename.lower().endswith(".jpg"):
                continue

            old_id = int(os.path.splitext(filename)[0])
            try:
                user = User.objects.get(old_id=old_id)
            except User.DoesNotExist:
                self.stdout.write(self.style.WARNING(f"User not found for old_id {old_id}"))
                continue

            profile = profile.objects.get(user=user)
            photo_path = os.path.join(path, filename)
            with open(photo_path, "rb") as f:
                profile.photo.save(
                    f"{user.id}".jpg,
                    File(f),
                    save=True
                )

            self.stdout.write(self.style.SUCCESS(f"Imported photo for {user.email}"))
            
        