from django import forms
from .models import Exec, Membership, Profile, PSG, Waiver
from django.contrib.auth import get_user_model

from .utils import *
import datetime

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'pronouns', 'phone', 'student_number', 'birthdate', 'blurb', 'acc', 'vocene', 'trip_org_email')

    first_name = forms.CharField(max_length=64, required=True)
    last_name = forms.CharField(max_length=64, required=True)
    pronouns = forms.CharField(max_length=32, required=False)
    phone = forms.CharField(max_length=32, required=True)
    student_number = forms.CharField(max_length=8, required=False)
    birthdate = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    blurb = forms.CharField(
        required=False,
        widget=forms.TextInput()
    )
    acc = forms.BooleanField(
        required=True,
        label="Would you like a membership in the Alpine Club of Canada (ACC) for no additional cost?",
        widget=forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')])
    )
    vocene = forms.BooleanField(
        required=True,
        label="Would you like to receive the VOCene (our ~monthly newsletter)?",
        widget=forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')])
    )
    trip_org_email = forms.BooleanField(
        required=True,
        label="Would you like to receive the trip organizer info email after posting a trip?",
        widget=forms.RadioSelect(choices=[(True, 'Yes'), (False, 'No')])
    )


class MembershipForm(forms.ModelForm):
    class Meta:
        model = Membership
        fields = ('start_date', 'end_date', 'type')

    start_date = forms.DateField(
        initial=datetime.datetime.today(),
        required=True,
        disabled=True
    )
    end_date = forms.DateField(
        initial=get_end_date(datetime.datetime.today()),
        required=True,
        disabled=True
    )
    type = forms.ChoiceField(
        choices=Membership.MembershipType.choices, 
        required=True,
        initial=Membership.MembershipType.REGULAR
    )

    def __init__(self, *args, **kwargs):
        """
        Any view that renders this form will need to pass in the current request.user to be used by the form
        This eliminates the need for 'user' to be a disabled field on the form
        """
        self.user = kwargs.pop('user', None)
        super(MembershipForm, self).__init__(*args, **kwargs)
        self.fields['type'].label = "Membership Type"

    def save(self, commit=True):
        membership = super(MembershipForm, self).save(commit=False)
        if self.user:
            membership.user = self.user
            if commit:
                membership.save()
        return membership
    
class WaiverForm(forms.ModelForm):
    class Meta:
        model = Waiver
        fields = ('full_name', 'student_number', 'guardian_name', 'signature')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        user_is_minor = is_minor(datetime.datetime.today(), user.profile.birthdate)
        if user_is_minor:
            self.fields['guardian_name'].required = True
        else:
            self.fields.pop('guardian_name')

    full_name = forms.CharField(max_length=128, required=True)
    student_number = forms.CharField(max_length=8, required=False)
    guardian_name = forms.CharField(max_length=128, required=False)
    signature = forms.CharField(required=False, widget=forms.HiddenInput())

class ExecForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Member Name",
        widget=forms.Select,
        required=True
    )
    exec_role = forms.CharField(max_length=32, required=True)

    class Meta:
        model = Exec
        fields = ('user', 'exec_role')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].label_from_instance = self.get_user_label

    def get_user_label(self, obj):
        profile = Profile.objects.get(user=obj)
        return f"{profile.first_name} {profile.last_name}"
    
class PSGForm(forms.ModelForm):
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="Member Name",
        widget=forms.Select,
        required=True
    )

    class Meta:
        model = PSG
        fields = ('user',)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].label_from_instance = self.get_user_label

    def get_user_label(self, obj):
        profile = Profile.objects.get(user=obj)
        return f"{profile.first_name} {profile.last_name}"
