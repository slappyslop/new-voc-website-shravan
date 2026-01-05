from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Exec, Membership, Profile, PSG, Waiver

from .utils import *

User = get_user_model()

class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('first_name', 'last_name', 'pronouns', 'phone', 'student_number', 'birthdate', 'bio', 'emergency_info', 'inreach_address', 'acc', 'vocene', 'trip_org_email', 'photo')
        labels = {
            "photo": "Profile Photo"
        }

    first_name = forms.CharField(max_length=64, required=True)
    last_name = forms.CharField(max_length=64, required=True)
    pronouns = forms.CharField(max_length=32, required=False)
    phone = forms.CharField(max_length=32, required=True)
    student_number = forms.CharField(max_length=8, required=False)
    birthdate = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    bio = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 5,'cols': 50})
    )
    emergency_info = forms.CharField(
        required=False,
        label="Example: Parents: Alice/Bob@604-123-4567; Wife: Carol@778-123-4567; Allergies: Bees (deadly, I carry an EpiPen)",
        widget=forms.Textarea(attrs={'rows': 2, 'cols': 50})
    )
    inreach_address = forms.CharField(
        required=False,
        label="inReach email/link"
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
        fields = ('type',)

    # start_date = forms.DateField(
    #     initial=datetime.datetime.today(),
    #     required=True,
    #     disabled=True
    # )
    # end_date = forms.DateField(
    #     initial=get_end_date(datetime.datetime.today()),
    #     required=True,
    #     disabled=True
    # )
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
            membership.start_date = timezone.localdate()
            membership.end_date = get_end_date(timezone.localdate())
            
            if commit:
                membership.save()
        return membership
    
class WaiverForm(forms.ModelForm):
    class Meta:
        model = Waiver
        fields = (
            'checkbox1', 
            'checkbox2', 
            'checkbox3', 
            'checkbox4', 
            'checkbox5',
            'checkbox6',
            'checkbox7',
            'full_name',
            'student_number',
            'guardian_name',
            'signature'
        )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        readonly = kwargs.pop('readonly', False)
        super().__init__(*args, **kwargs)

        user_is_minor = is_minor(timezone.localdate(), user.profile.birthdate)
        if user_is_minor:
            self.fields['guardian_name'].required = True
        else:
            self.fields.pop('guardian_name')

        if readonly:
            for field_name, field in self.fields.items():
                field.disabled = True
            for checkbox in ['checkbox1', 'checkbox2', 'checkbox3', 'checkbox4', 'checkbox5', 'checkbox6', 'checkbox7']:
                self.fields[checkbox].initial = True
            self.fields["i_agree_text"].initial = "I AGREE"

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')

        if not signature or 'data:image' not in signature:
            raise forms.ValidationError("Signature is required")
        
        return signature

    checkbox1 = forms.BooleanField(label="There are several checkboxes throughout this document - PLEASE READ AND CHECK THEM ALL.", required=True)
    checkbox2 = forms.BooleanField(label="I UNDERSTAND THE ABOVE AND AGREE TO READ THE FULL TEXT BELOW.", required=True)
    checkbox3 = forms.BooleanField(label="I AM AWARE OF THE RISKS AND AGREE TO THE ABOVE.", required=True)
    checkbox4 = forms.BooleanField(label="I AM AWARE OF EVACUATION RESPONSIBILITIES AND AGREE TO THE ABOVE.", required=True)
    checkbox5 = forms.BooleanField(label="I HAVE READ AND AGREE TO THE RESPONSIBILITIES STATED ABOVE.", required=True)
    checkbox6 = forms.BooleanField(label="I HAVE READ THE ABOVE AND AGREE TO IT.", required=True)
    checkbox7 = forms.BooleanField(label="I AGREE TO ALL OF THE ABOVE.", required=True)
    i_agree_text = forms.CharField(max_length=8, required=True)

    full_name = forms.CharField(max_length=128, required=True)
    student_number = forms.CharField(max_length=8, required=False)
    guardian_name = forms.CharField(max_length=128, required=False)
    signature = forms.CharField(required=False, widget=forms.HiddenInput())
