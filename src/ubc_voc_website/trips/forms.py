from django import forms
from .models import Trip, TripSignup, TripTag
from membership.models import Membership, Profile

from django.contrib.auth import get_user_model
import datetime

from django_quill.forms import QuillFormField

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

    def clean(self):
        """
        Conditional required fields for signup/pretrip details
        ie. signup related fields are required if and only if use_signup == True
        """
        cleaned_data = super().clean()
        use_signup, use_pretrip = cleaned_data.get('use_signup'), cleaned_data.get('use_pretrip')

        if use_signup:
            required_fields = [
                'signup_question',
                'max_participants',
                'interested_start',
                'interested_end',
                'committed_start',
                'committed_end'
            ]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required when 'Use signup' is selected")

        if use_pretrip:
            required_fields = [
                'pretrip_time',
                'pretrip_location'
            ]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required when 'Use pretrip' is selected")

    def save(self, commit=True, user=None):
        trip = super().save(commit=False)
        if commit:
            trip.save()
            if 'tags' in self.cleaned_data:
                trip.tags.set(self.cleaned_data['tags'])

            if user and not trip.organizers.filter(pk=user.pk).exists():
                trip.organizers.add(user)

        return trip

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
        required=False,
        label="Additional Organizers",
        widget=forms.SelectMultiple(attrs={'class': 'choices'})
    )
    start_time = forms.DateTimeField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'flatpickr'})
    )
    end_time = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'flatpickr'})
    )
    published = forms.BooleanField(
        initial=False,
        required=False,
        label="Publish this trip on the trip agenda? (leave unchecked if you would like to edit this trip later before posting it)"
    )
    status = forms.ChoiceField(
        choices=Trip.TripStatus.choices,
        required=True,
        label="Is this trip tentative/cancelled?"
    )
    tags = forms.ModelMultipleChoiceField(
        queryset=TripTag.objects.all(),
        required=False,
        label="Tags",
        widget=forms.SelectMultiple(attrs={'class': 'choices'})
    )
    description = QuillFormField()
    use_signup = forms.BooleanField(
        initial=False,
        required=False,
        label="Use the trip signup tools"
    )
    signup_question = forms.CharField(
        max_length=256, 
        required=False
    )
    max_participants = forms.IntegerField(
        required=False
    )
    interested_start = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'flatpickr'})
    )
    interested_end = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'flatpickr'})
    )
    committed_start = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'flatpickr'})
    )
    committed_end = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'flatpickr'})
    )
    use_pretrip = forms.BooleanField(
        initial=False,
        required=False
    )
    pretrip_time = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'flatpickr'})
    )
    pretrip_location = forms.CharField(
        max_length=128, 
        required=False
    )
    drivers_required = forms.BooleanField(
        initial=False,
        required=False
    )

class TripSignupForm(forms.ModelForm):
    class Meta:
        model = TripSignup
        fields = ('type', 'can_drive', 'car_spots', 'signup_answer')

    def __init__(self, *args, trip, **kwargs):
        super().__init__(*args, **kwargs)

        signup_choices = trip.valid_signup_types
        if not signup_choices:
            self.fields.pop('type')
        else:
            self.fields['type'].choices = [(choice.value, choice.label) for choice in signup_choices]

        print(trip.signup_question)
        if not trip.signup_question:
            self.fields.pop('signup_answer')
        else:
            self.fields['signup_answer'].label_from_instance = trip.signup_question

    type = forms.ChoiceField(
        required=True
    )
    can_drive = forms.BooleanField(initial=False)
    car_spots = forms.IntegerField(required=False)
    signup_answer = forms.CharField(max_length=256, required=False)
