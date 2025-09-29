from django import forms
from membership.models import Profile
from .models import Book, BookRental, CancelledGearHour, Gear, GearHour, GearRental

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

    def save(self, commit=True):
        gear_hour = super().save(commit=False)
        if self.user:
            gear_hour.qm = self.user

        if commit:
            gear_hour.save()

        return gear_hour

    start_date = forms.DateField(
        required=True,
        initial=datetime.datetime.today(),
        widget=forms.TextInput(attrs={'class': 'flatpickr-date'})
    )
    end_date = forms.DateField(
        required=True,
        widget=forms.TextInput(attrs={'class': 'flatpickr-date'})
    )
    start_time = forms.TimeField(
        required=True,
        initial=datetime.datetime.now().strftime('%I:%M %p'),
        input_formats=['%I:%M %p'],
        widget=forms.TextInput(attrs={'class': 'flatpickr-timeonly'})
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

class GearRentalForm(forms.ModelForm):
    class Meta:
        model = GearRental
        fields = (
            'member',
            # 'gear',
            'deposit',
            'start_date',
            'due_date',
            'notes',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].label_from_instance = self.get_profile_label

    @staticmethod
    def get_profile_label(user):
        try:
            return user.profile.full_name
        except Profile.DoesNotExist:
            return user.email

    member = forms.ModelChoiceField(
        queryset=User.objects.filter(membership__active=True).distinct().exclude(membership__type__in=["H", "I"]), # Exclude both types of honorary members
        label="Member Name",
        widget=forms.Select(attrs={"id": "member-select"}),
        required=True
    )
    # TODO make this field required when Gear objects have been added to the database
    # gear = forms.ModelMultipleChoiceField(
    #     queryset=Gear.objects.all(),
    #     label="Item(s) being rented",
    #     widget=forms.SelectMultiple(attrs={'class': 'choices'})
    # )
    # TODO once gear items are added, make the deposit calculation automatic
    deposit = forms.IntegerField()
    start_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today
    )
    due_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today() + datetime.timedelta(days=7)
    )
    notes = forms.TextInput()

class BookRentalForm(forms.ModelForm):
    class Meta:
        model = BookRental
        fields = (
            'member',
            # 'books',
            'deposit',
            'start_date',
            'due_date',
            'notes',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].label_from_instance = self.get_profile_label

    @staticmethod
    def get_profile_label(user):
        try:
            return user.profile.full_name
        except Profile.DoesNotExist:
            return user.email
        
    member = forms.ModelChoiceField(
        queryset=User.objects.filter(membership__active=True).distinct(),
        label="Member Name",
        widget=forms.Select,
        required=True
    )
    # TODO make this field required when books have been added to the database (large project)
    # books = forms.ModelMultipleChoiceField(
    #     queryset=Book.objects.all(),
    #     label="Item(s) being rented",
    #     widget=forms.SelectMultiple(attrs={'class': 'choices'})
    # )
    # TODO once gear items are added, make the deposit calculation automatic
    deposit = forms.IntegerField()
    start_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today
    )
    due_date = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today() + datetime.timedelta(days=7)
    )
    notes = forms.TextInput()

