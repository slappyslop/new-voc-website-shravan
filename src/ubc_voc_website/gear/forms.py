from django import forms
from .models import GearHour, CancelledGearHour

from django.contrib.auth import get_user_model

import datetime

User = get_user_model()

class GearHourForm(forms.ModelForm):
    class Meta:
        model = GearHour
        fields = (
            'start_date',
            'end_date',
            'start_time',
            'duration'
        )

    def __init__(self, *args, gear_hour=None, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.gear_hour = gear_hour

    start_date = forms.DateField(
        required=True,
        initial=datetime.datetime.today(),
        widget=forms.TextInput(attrs={'class': 'flatpickr'})
    )
    end_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'flatpickr'})
    )
    start_time = forms.TimeField(
        required=True,
        initial=datetime.datetime.now().time()
    )
    duration = forms.IntegerField(
        required=True,
        initial=60
    )


class CancelledGearHourForm(forms.ModelForm):
    class Meta:
        model = CancelledGearHour
        fields = (
            'gear_hour',
            'date'
        )

    gear_hour = forms.ModelChoiceField(
        queryset=GearHour.objects.all(),
        label="Gear Hour",
        widget=forms.Select,
        required=True
    )

    date = forms.DateField(
        required=True
    )
