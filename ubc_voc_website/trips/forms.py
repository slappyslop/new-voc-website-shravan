from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Trip, TripSignup, TripTag
from membership.models import Profile

from django_quill.forms import QuillFormField

User = get_user_model()

class TripForm(forms.ModelForm):
    SIGNUP_START_CHOICES = [
        ("never", "Never"),
        ("now", "Now"),
        ("custom", "Custom")
    ]

    SIGNUP_END_CHOICES = [
        ("pretrip", "The pretrip meeting"),
        ("trip", "The trip itself"),
        ("custom", "Custom")
    ]

    class Meta:
        model = Trip
        fields = (
            'name',
            # 'organizers',
            'start_time', 
            'end_time',
            'in_clubroom',
            'status',
            'description',
            'members_only_info',
            'use_signup',
            'signup_question',
            'max_participants',
            'interested_start_choice',
            'interested_start',
            'interested_end_choice',
            'interested_end',
            'committed_start_choice',
            'committed_start',
            'committed_end_choice',
            'committed_end',
            'going_start_choice',
            'going_start',
            'going_end_choice',
            'going_end',
            'use_pretrip',
            'pretrip_time',
            'pretrip_location',
            'drivers_required'
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        instance = kwargs.get('instance')
        super().__init__(*args, **kwargs)
        # self.fields['organizers'].label_from_instance = self.get_profile_label

        if instance and instance.pk:
            self.fields['tags'].initial = instance.tags.all()
            # self.fields['organizers'].initial = instance.organizers.exclude(pk=user.pk)

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
            interested_start_choice = cleaned_data.get("interested_start_choice")
            if interested_start_choice == "never":
                cleaned_data["interested_start"] = None
            elif interested_start_choice == "now":
                cleaned_data["interested_start"] = timezone.now()
            else:
                interested_start_custom = cleaned_data.get("interested_start")
                if not interested_start_custom:
                    self.add_error("interested_start", "Please choose a date and time")
                else:
                    cleaned_data["interested_start"] = interested_start_custom

            if not cleaned_data["interested_start"]:
                cleaned_data["interested_end"] = None
            else:
                interested_end_choice = cleaned_data.get("interested_end_choice")
                if interested_end_choice == "pretrip":
                    if not cleaned_data.get("use_pretrip"):
                        self.add_error("interested_end_choice", "Trip does not have a pretrip meeting")
                    else:
                        cleaned_data["interested_end"] = cleaned_data.get("pretrip_time")
                elif interested_end_choice == "trip":
                    cleaned_data["interested_end"] = cleaned_data.get("start_time")
                else:
                    interested_end_custom = cleaned_data.get("interested_end")
                    if not interested_end_custom:
                        self.add_error("interested_end", "Please choose a date and time")
                    else:
                        cleaned_data["interested_end"] = interested_end_custom

            committed_start_choice = cleaned_data.get("committed_start_choice", "never")
            if committed_start_choice == "never":
                cleaned_data["committed_start"] = None
            elif committed_start_choice == "now":
                cleaned_data["committed_start"] = timezone.now()
            else:
                committed_start_custom = cleaned_data.get("committed_start")
                if not committed_start_custom:
                    self.add_error("committed_start", "Please choose a date and time")
                else:
                    cleaned_data["committed_start"] = committed_start_custom

            if not cleaned_data.get("committed_start", None):
                cleaned_data["committed_end"] = None
            else:
                committed_end_choice = cleaned_data.get("committed_end_choice")
                if committed_end_choice == "pretrip":
                    if not cleaned_data.get("use_pretrip"):
                        self.add_error("committed_end_choice", "Trip does not have a pretrip meeting")
                    else:
                        cleaned_data["committed_end"] = cleaned_data.get("pretrip_time")
                elif committed_end_choice == "trip":
                    cleaned_data["committed_end"] = cleaned_data.get("start_time")
                else:
                    committed_end_custom = cleaned_data.get("committed_end")
                    if not committed_end_custom:
                        self.add_error("committed_end", "Please choose a date and time")
                    else:
                        cleaned_data["committed_end"] = committed_end_custom

            going_start_choice = cleaned_data.get("going_start_choice")
            if going_start_choice == "never":
                cleaned_data["going_start"] = None
            elif going_start_choice == "now":
                cleaned_data["going_start"] = timezone.now()
            else:
                going_start_custom = cleaned_data.get("going_start")
                if not going_start_custom:
                    self.add_error("going_start", "Please choose a date and time")
                else:
                    cleaned_data["going_start"] = going_start_custom

            if not cleaned_data["going_start"]:
                cleaned_data["going_end"] = None
            else:
                going_end_choice = cleaned_data.get("going_end_choice")
                if going_end_choice == "pretrip":
                    if not cleaned_data.get("use_pretrip"):
                        self.add_error("going_end_choice", "Trip does not have a pretrip meeting")
                    else:
                        cleaned_data["going_end"] = cleaned_data.get("pretrip_time")
                elif going_end_choice == "trip":
                    cleaned_data["going_end"] = cleaned_data.get("start_time")
                else:
                    going_end_custom = cleaned_data.get("going_end")
                    if not going_end_custom:
                        self.add_error("going_end", "Please choose a date and time")
                    else:
                        cleaned_data["going_end"] = going_end_custom

        if use_pretrip:
            required_fields = [
                'pretrip_time',
                'pretrip_location'
            ]
            for field in required_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, "This field is required when 'Use pretrip' is selected")

        return cleaned_data

    def save(self, commit=True, user=None):
        trip = super().save(commit=False)
        if commit:
            trip.save()
            if 'tags' in self.cleaned_data:
                trip.tags.set(self.cleaned_data['tags'])
            # if 'organizers' in self.cleaned_data:
            #     trip.organizers.set(self.cleaned_data['organizers'])

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
        label="Trip/Event Name"    
    )
    # organizers = forms.ModelMultipleChoiceField(
    #     queryset=User.objects.filter(id__in=Membership.objects.filter(
    #         active=True,
    #         end_date__gte=datetime.date.today()
    #     )),
    #     required=False,
    #     label="Additional Organizers",
    #     widget=forms.SelectMultiple(attrs={'class': 'choices'})
    # )
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
    description = QuillFormField(
        label="Trip Description"
    )
    members_only_info = forms.CharField(
        max_length=1024,
        required=False,
        label="Info that should be shown only to VOC Members (eg. WhatsApp group link, spreadsheet, etc.)"
    )
    use_signup = forms.BooleanField(
        initial=True,
        required=False,
        label="Use the trip signup tools"
    )
    signup_question = forms.CharField(
        max_length=1024, 
        required=False,
        label="Question to ask participants when they sign up",
    )
    max_participants = forms.IntegerField(
        required=False,
        label="What is the (estimated) maximum number of participants"
    )
    interested_start_choice = forms.ChoiceField(
        choices=SIGNUP_START_CHOICES,
        widget=forms.RadioSelect,
        initial="custom"
    ) 
    interested_start = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'flatpickr'}),
        label=""
    )
    interested_end_choice = forms.ChoiceField(
        choices=SIGNUP_END_CHOICES,
        widget=forms.RadioSelect,
        initial="custom"
    )
    interested_end = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'flatpickr'}),
        label=""
    )
    committed_start_choice = forms.ChoiceField(
        choices=SIGNUP_START_CHOICES,
        widget=forms.RadioSelect,
        initial="custom"
    ) 
    committed_start = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'flatpickr'}),
        label=""
    )
    committed_end_choice = forms.ChoiceField(
        choices=SIGNUP_END_CHOICES,
        widget=forms.RadioSelect,
        initial="custom"
    )
    committed_end = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'flatpickr'}),
        label=""
    )
    going_start_choice = forms.ChoiceField(
        choices=SIGNUP_START_CHOICES,
        widget=forms.RadioSelect,
        initial="never"
    )
    going_start = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'flatpickr'}),
        label=""
    )
    going_end_choice = forms.ChoiceField(
        choices=SIGNUP_END_CHOICES,
        widget=forms.RadioSelect,
        initial="custom"
    )
    going_end = forms.DateTimeField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'flatpickr'}),
        label=""
    )
    use_pretrip = forms.BooleanField(
        initial=True,
        required=False,
        label="Are you holding a pretrip meeting?"
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
        required=False,
        label="Ask prospective participants if they can drive?"
    )

class TripSignupForm(forms.ModelForm):
    class Meta:
        model = TripSignup
        fields = ('type', 'can_drive', 'car_spots', 'signup_answer')

    def __init__(self, *args, user=None, trip=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.user = user
        self.trip = trip

        if self.instance and self.instance.pk:
            self.fields.pop("type", None)
        else:
            signup_choices = self.trip.valid_signup_types
            if not signup_choices:
                self.fields.pop('type')
            else:
                self.fields['type'].choices = [(choice.value, choice.label) for choice in signup_choices]

        if not getattr(self.trip, "signup_question", None):
            self.fields.pop('signup_answer', None)
        else:
            self.fields['signup_answer'].label = self.trip.signup_question

        if not getattr(self.trip, "drivers_required", None):
            self.fields.pop('can_drive', None)
            self.fields.pop('car_spots', None)

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('can_drive') and not cleaned_data.get('car_spots'):
            self.add_error('car_spots', "This field is required when 'Can drive' is selected")
        return cleaned_data

    def save(self, commit=True):
        signup = super().save(commit=False)

        signup.user = self.user
        signup.trip = self.trip

        if self.instance.pk:
            signup.type = self.instance.type
        else:
            signup.type = int(self.cleaned_data.get("type"))
            if int(signup.type) not in signup.trip.valid_signup_types:
                raise forms.ValidationError("The selected signup option is not currently available for this trip")

        fields = ["can_drive", "car_spots", "signup_answer"]
        for field in fields:
            if field in self.cleaned_data:
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
