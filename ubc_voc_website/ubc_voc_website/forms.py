from django import forms
from allauth.account.forms import SignupForm
from membership.models import Profile
    
class CustomSignupForm(SignupForm):
    first_name = forms.CharField(max_length=64, required=True)
    last_name = forms.CharField(max_length=64, required=True)
    pronouns = forms.CharField(max_length=32, required=False)
    phone = forms.CharField(max_length=32, required=True)
    student_number = forms.CharField(max_length=8, required=False)
    birthdate = forms.DateField(required=True, widget=forms.DateInput(attrs={'type': 'date'}))

    def save(self, request):
        user = super().save(request)

        Profile.objects.create(
            user=user,
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            pronouns=self.cleaned_data['pronouns'],
            phone=self.cleaned_data['phone'],
            student_number=self.cleaned_data['student_number'],
            birthdate=self.cleaned_data['birthdate']
        )

        return user