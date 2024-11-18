from django import forms
from .models import Car, Trip, TripSignup
from membership.models import Membership

from django.contrib.auth import get_user_model

User = get_user_model()

class TripForm(forms.ModelForm):
    class Meta:
        model = Trip
        fields = (
            'name',
            'organizers',
            'start_time', 
            'end_time', 
            'published',
            'status',
            'description',
            'use_signup',
            'signup_question',
            'max_participants',
            'interested_start',
            'interested_end',
            'committed_start',
            'committed_end',
            'use_pretrip',
            'pretrip_time',
            'pretrip_location',
            'drivers_required'
        )

    name = forms.CharField(max_length=256, required=True)
    organizers = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(user__in=Membership.objects.filter(mapped_status="Active").values('user')),
        label="Organizers",
        widget=forms.SelectMultiple(),
        required=True
    )
    start_time = forms.DateTimeField(required=True)
    end_time = forms.DateTimeField(required=True)
    published = forms.BooleanField(default=False)
    status = forms.ChoiceField(
        choices=Trip.TripStatus.choices,
        required=True
    )
    description = forms.CharField(
        required=True,
        widget=forms.TextInput()
    )
    use_signup = forms.BooleanField(default=False)
    signup_question = forms.CharField(max_length=256, required=False)
    max_participants = forms.IntegerField(required=True)
    interested_start = forms.DateTimeField(required=True)
    interested_end = forms.DateTimeField(required=True)
    committed_start = forms.DateTimeField(required=True)
    committed_end = forms.DateTimeField(required=True)
    use_pretrip = forms.BooleanField(default=False)
    pretrip_time = forms.DateTimeField(required=True)
    pretrip_location = forms.CharField(max_length=128, required=True)
    drivers_required = forms.BooleanField(default=False)

class TripSignupForm(forms.ModelForm):
    class Meta:
        model = TripSignup
        fields = ('type', 'can_drive', 'signup_answer')

    type = forms.ChoiceField(
        choices=TripSignup.TripSignupTypes.choices,
        required=True
    )
    can_drive = forms.BooleanField(default=False)
    signup_answer = forms.CharField(max_length=256, required=False)

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ('seats')

    seats = forms.IntegerField(required=True)
    
