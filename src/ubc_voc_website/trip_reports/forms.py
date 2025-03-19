from django import forms
from .models import TripReport
from membership.models import Membership
from trips.models import Trip

from django.contrib.auth import get_user_model
User = get_user_model()

import datetime
from django_quill.forms import QuillFormField

class TripReportForm(forms.ModelForm):
    class Meta:
        model = TripReport
        fields = (
            'trip',
            'title',
            'authors',
            'content'
        )

    trip = forms.ModelChoiceField(
        queryset=Trip.objects.filter(start_time__lte=datetime.datetime.now()),
        required=False,
        label="Trip",
        empty_label=None,
        widget=forms.Select(attrs={'class': 'choices'})
    )
    title = forms.CharField(
        max_length=256,
        required=True,
        label="Title",
        widget=forms.TextInput(attrs={
            'class': 'form-control'
        })
    )
    authors = forms.ModelMultipleChoiceField(
        queryset=User.objects.filter(id__in=Membership.objects.filter(
            active=True,
            end_date__gte=datetime.date.today()
        )),
        required=False,
        label="Additional Authors",
        widget=forms.SelectMultiple(attrs={'class': 'choices'})
    )
    content = QuillFormField()