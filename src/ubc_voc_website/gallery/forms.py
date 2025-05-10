from django import forms

from photologue.models import Photo

class UserPhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'image', 'caption']

    def __init__(self, *args, user=None, **kwargs):
        self.user = user
        super().__init__(*args, *kwargs)

    def clean_title(self):
        original_title = self.cleaned_data['title']
        full_title = f"user{self.user.id}:{original_title}"

        if Photo.objects.filter(title=full_title).exists():
            raise forms.ValidationError("You already have a photo with this title")
        
        return full_title