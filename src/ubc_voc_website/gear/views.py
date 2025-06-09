from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required

from .models import GearHour, CancelledGearHour, BookRental, GearRental
from .forms import GearHourForm
from membership.models import Profile
from ubc_voc_website.decorators import Admin, Members, Execs

import datetime
import pytz
import json

pacific = pytz.timezone('America/Vancouver')

User = get_user_model()

@Members
def gear_hours(request):
    if request.POST:
        form = GearHourForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)
        
    gear_hours = GearHour.objects.filter(start_date__lte=datetime.date.today(), end_date__gte=datetime.date.today())
    cancelled_gear_hours = CancelledGearHour.objects.filter(gear_hour__in=gear_hours)

    calendar_events = []
    for gear_hour in gear_hours:
        qm_name = Profile.objects.get(user=gear_hour.qm).first_name

        date = gear_hour.start_date
        while date <= gear_hour.end_date:
            if not cancelled_gear_hours.filter(gear_hour=gear_hour, date=date).exists():
                start_datetime = datetime.datetime.combine(date, gear_hour.start_time)
                start_datetime = pacific.localize(start_datetime)
                end_datetime = start_datetime + datetime.timedelta(minutes=gear_hour.duration)

                calendar_events.append({
                    'id': f"{gear_hour.id}: {date}",
                    'title': f"Gear Hours - {qm_name}",
                    'start': start_datetime.isoformat(),
                    'end': end_datetime.isoformat()
                })
            date = date + datetime.timedelta(days=7)

    form = GearHourForm(user=request.user)

    return render(request, 'gear/gear_hours.html', {
        'gear_hours': json.dumps(calendar_events),
        'form': form,
    })

@Execs
def delete_gear_hour(request, id):
    if request.method == "POST":
        gear_hour = get_object_or_404(GearHour, id=id)

        body = json.loads(request.body)
        delete_all = body.get('delete_all')
        date = body.get('date')
        date = datetime.datetime.fromisoformat(date).date()

        if delete_all: # delete the entire gear hour instance
            gear_hour.delete()
        else: # add a CancelledGearHour instance for this date
            CancelledGearHour.objects.create(
                gear_hour = gear_hour,
                date = date
            )

    return redirect('gear_hours')

@Execs
def gear_rentals(request):
    gear_rentals = GearRental.objects.all()
    book_rentals = BookRental.objects.all()

    current_gear_rentals = gear_rentals.filter(returned=False)
    current_book_rentals = book_rentals.filter(returned=False)

    overdue_gear_rentals = current_gear_rentals.filter(due_date__lt=datetime.datetime.today())
    overdue_book_rentals = current_book_rentals.filter(due_date__lte=datetime.datetime.today())

    return render(request, 'gear/gearmaster.html')

@Execs
def create_gear_rental(request):
    pass

@Execs
def edit_gear_rental(request, pk):
    pass

@Execs
def renew_gear_rental(request, pk):
    pass

@Execs
def return_gear_rental(request, pk):
    pass

@Execs
def lost_gear_rental(request, pk):
    pass
