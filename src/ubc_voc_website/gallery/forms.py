from django import forms

from photologue.models import Photo

class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'image', 'caption']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

class UserPhotoUploadForm(PhotoUploadForm):
    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, *kwargs)

    def clean_title(self):
        original_title = self.cleaned_data['title']
        full_title = f"user{self.user.id}:{original_title}"

        if Photo.objects.filter(title=full_title).exists():
            raise forms.ValidationError("You already have a photo with this title")
        
        return full_title
    
class TripPhotoUploadForm(PhotoUploadForm):
    def __init__(self, *args, trip=None, **kwargs):
        self.trip = trip
        super().__init__(*args, **kwargs)

    def clean_title(self):
        original_title = self.cleaned_data['title']
        full_title = f"trip{self.trip.id}:{original_title}"

        if Photo.objects.filter(title=full_title).exists():
            raise forms.ValidationError("The trip already has a photo with this title")

        return full_title