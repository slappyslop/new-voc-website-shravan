from django import forms
from .models import Car, Trip, TripSignup
from membership.models import Membership, Profile

from django.contrib.auth import get_user_model
import datetime

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organizers'].label_from_instance = self.get_profile_label

    @staticmethod
    def get_profile_label(user):
        try:
            profile = Profile.objects.get(user=user)
            return f"{profile.first_name} {profile.last_name}"
        except Profile.DoesNotExist:
            return user.email

    name = forms.CharField(
        max_length=256, 
        required=True,
        label="Trip Name"    
    )
    organizers = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(id__in=Membership.objects.filter(
            active=True,
            end_date__gte=datetime.date.today()
        )),
        label="Additional Organizers",
        widget=forms.SelectMultiple(attrs={'class': 'choices'})
    )
    start_time = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )
    end_time = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )
    published = forms.BooleanField(
        initial=False,
        label="Publish this trip on the trip agenda? (leave blank if you would like to edit this trip later before posting it)"
    )
    status = forms.ChoiceField(
        choices=Trip.TripStatus.choices,
        required=True,
        label="Is this trip tentative/cancelled?"
    )
    description = forms.CharField(
        required=True,
        widget=forms.Textarea(attrs={
            'class': 'rich-textbox',
            'rows': 10,
            'cols': 80
        }),
        label="Trip Description"
    )
    use_signup = forms.BooleanField(
        initial=False,
        label="Use the trip signup tools"
    )
    signup_question = forms.CharField(
        max_length=256, 
        required=False
    )
    max_participants = forms.IntegerField(
        required=True
    )
    interested_start = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )
    interested_end = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )
    committed_start = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )
    committed_end = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )
    use_pretrip = forms.BooleanField(
        initial=False
    )
    pretrip_time = forms.DateTimeField(
        required=True,
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
    )
    pretrip_location = forms.CharField(
        max_length=128, 
        required=True
    )
    drivers_required = forms.BooleanField(
        initial=False
    )

class TripSignupForm(forms.ModelForm):
    class Meta:
        model = TripSignup
        fields = ('type', 'can_drive', 'signup_answer')

    type = forms.ChoiceField(
        choices=TripSignup.TripSignupTypes.choices,
        required=True
    )
    can_drive = forms.BooleanField(initial=False)
    signup_answer = forms.CharField(max_length=256, required=False)

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ('seats',)

    seats = forms.IntegerField(required=True)
    
