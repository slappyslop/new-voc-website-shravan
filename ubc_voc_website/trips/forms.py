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
            'in_clubroom',
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
        user = kwargs.pop('user', None)
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        self.fields['organizers'].label_from_instance = self.get_profile_label

        if instance and instance.pk:
            self.fields['tags'].initial = instance.tags.all()
            self.fields['organizers'].initial = instance.organizers.exclude(pk=user.pk)

    def clean(self):
        """
        Conditional required fields for signup/pretrip details
        ie. signup related fields are required if and only if use_signup == True
        """
        cleaned_data = super().clean()
        in_clubroom, use_signup, use_pretrip = cleaned_data.get('in_clubroom'), cleaned_data.get('use_signup'), cleaned_data.get('use_pretrip')

        if in_clubroom:
            if not cleaned_data.get('end_time'):
                self.add_error('end_time', """End time is required for clubroom events to keep our clubroom calendar up to date.
                               This is not a booking, it just gives us an idea of when the clubroom is being used - 
                               so if you don't know the exact end time, just give your best guess""")
        
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
            return user.profile.full_name
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
    in_clubroom = forms.BooleanField(
        initial=False,
        required=False,
        label="Will this event happen in the clubroom?"
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

    def __init__(self, *args, trip=None, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        self.trip = trip

        try:
            self.signup = TripSignup.objects.get(user=self.user, trip=self.trip)
            for field in self.fields:
                if hasattr(self.signup, field):
                    self.fields[field].initial = getattr(self.signup, field)
        except TripSignup.DoesNotExist:
            self.signup = None
        
        signup_choices = self.trip.valid_signup_types
        if not signup_choices:
            self.fields.pop('type')
        else:
            self.fields['type'].choices = [(choice.value, choice.label) for choice in signup_choices]

        if not self.trip.signup_question:
            self.fields.pop('signup_answer')
        else:
            self.fields['signup_answer'].label_from_instance = self.trip.signup_question

    def clean(self):
        cleaned_data = super().clean()
        can_drive = cleaned_data.get('can_drive')
        if can_drive and not cleaned_data.get('car_spots'):
            self.add_error('car_spots', "This field is required when 'Use signup' is selected")

    def save(self, commit=True):
        try:
            signup = TripSignup.objects.get(user=self.user, trip=self.trip)
        except TripSignup.DoesNotExist:
            signup = super().save(commit=False)
            signup.user = self.user
            signup.trip = self.trip

        for field in self.cleaned_data:
            setattr(signup, field, self.cleaned_data[field])

        if commit:
            signup.save()
        return signup

    type = forms.ChoiceField(
        required=True
    )
    can_drive = forms.BooleanField(initial=False, required=False)
    car_spots = forms.IntegerField(required=False)
    signup_answer = forms.CharField(max_length=256, required=False)
