from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .models import GearHour, CancelledGearHour
from ubc_voc_website.decorators import Admin, Members, Execs

import datetime

User = get_user_model()

@Members
def gear_hours(request):
    gear_hours = GearHour.objects.filter(end_date__gte=datetime.date.today())
    return render(request, 'gear/gear_hours.html', {'gear_hours': gear_hours})

@Execs
def create_gear_hour(request):
    pass

@Execs
def edit_gear_hour(request):
    pass
