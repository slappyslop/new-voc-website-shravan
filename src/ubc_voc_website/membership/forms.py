from django import forms
from .models import Membership, Waiver

from .utils import *
import datetime

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
        fields = ('full_name', 'student_number', 'guardian_name', 'paper_waiver')

    full_name = forms.CharField(max_length=128, required=True)
    student_number = forms.CharField(max_length=8, required=False)
    guardian_name = forms.CharField(max_length=128, required=False)
    # signature = forms.ImageField(required=True)
    paper_waiver = forms.BooleanField()




    

