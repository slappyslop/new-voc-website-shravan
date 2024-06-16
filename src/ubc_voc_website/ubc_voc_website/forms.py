from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
from membership.models import Profile

class CustomUserCreationForm(UserCreationForm):
    firstname = forms.CharField(max_length=64, required=True)
    lastname = forms.CharField(max_length=64, required=True)
    pronouns = forms.CharField(max_length=32, required=False)
    phone = forms.CharField(max_length=32, required=True)
    student_number = forms.CharField(max_length=8, required=False)
    birthdate = forms.DateField(required=False)

    class Meta:
        model = User
        fields = ('email', 'firstname', 'lastname', 'pronouns', 'phone', 'student_number', 'birthdate')

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                firstname=self.cleaned_data['firstname'],
                lastname=self.cleaned_data['lastname'],
                pronouns=self.cleaned_data['pronouns'],
                phone=self.cleaned_data['phone'],
                student_number=self.cleaned_data['student_number'],
                birthdate=self.cleaned_data['birthdate']
            )
        return user