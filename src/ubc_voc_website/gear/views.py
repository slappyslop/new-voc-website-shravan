from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .models import GearHour, CancelledGearHour
from membership.models import Profile
from ubc_voc_website.decorators import Admin, Members, Execs

import datetime
import json

User = get_user_model()

@Members
def gear_hours(request):
    gear_hours = GearHour.objects.filter(start_date__lte=datetime.date.today(), end_date__gte=datetime.date.today())
    cancelled_gear_hours = CancelledGearHour.objects.filter(gear_hour__in=gear_hours)

    calendar_events = []
    for gear_hour in gear_hours:
        qm_name = Profile.objects.get(user=gear_hour.qm).first_name

        date = gear_hour.start_date
        while date <= gear_hour.end_date:
            if not cancelled_gear_hours.filter(gear_hour=gear_hour, date=date).exists():
                start_time = datetime.datetime.combine(date, gear_hour.start_date.time())
                end_time = start_time + datetime.timedelta(minutes=gear_hour.duration)
                calendar_events.append({
                    'id': f"{gear_hour.id}: {date}",
                    'title': f"Gear Hours - {qm_name}",
                    'start': start_time,
                    'end': end_time
                })

    return render(request, 'gear/gear_hours.html', {'gear_hours': json.dumps(calendar_events)})

@Execs
def create_gear_hour(request):
    pass

@Execs
def edit_gear_hour(request):
    pass
