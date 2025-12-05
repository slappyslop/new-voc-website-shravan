from django.http import Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import GearHour, CancelledGearHour, BookRental, GearRental
from .forms import BookRentalForm, GearHourForm, GearRentalForm
from membership.models import Profile
from ubc_voc_website.decorators import Execs

import datetime
import pytz
import json

pacific = pytz.timezone('America/Vancouver')

User = get_user_model()

def gear_hours(request):
    if request.POST:
        if "delete" in request.POST:
            gear_hour_id = request.POST.get("gear-hour-id")
            delete_all = request.POST.get("delete-all") == "true"
            gear_hour = get_object_or_404(GearHour, id=gear_hour_id)

            if delete_all:
                gear_hour.delete()
            else:
                date = request.POST.get("date")
                CancelledGearHour.objects.create(
                    gear_hour = gear_hour,
                    date = date
                )
            return redirect('gear_hours')
        else:
            form = GearHourForm(request.POST, user=request.user)
            if form.is_valid():
                form.save()
            else:
                print(form.errors)
            return redirect('gear_hours')
    else:
        gear_hours = GearHour.objects.filter(start_date__lte=timezone.localdate(), end_date__gte=timezone.localdate())
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
def rentals(request):
    today = timezone.localdate()

    all_gear_rentals = list(GearRental.objects.all())
    for rental in all_gear_rentals:
        rental.type = "gear"
    current_gear_rentals = [rental for rental in all_gear_rentals if not rental.return_date and not rental.lost]
    overdue_gear_rentals = [rental for rental in current_gear_rentals if rental.due_date < today]
    long_gear_rentals = [rental for rental in overdue_gear_rentals if rental.due_date < (today - datetime.timedelta(weeks=3))]

    all_book_rentals = list(BookRental.objects.all())
    for rental in all_book_rentals:
        rental.type = "book"
    current_book_rentals = [rental for rental in all_book_rentals if not rental.return_date and not rental.lost]
    overdue_book_rentals = [rental for rental in current_book_rentals if rental.due_date < today]
    long_book_rentals = [rental for rental in overdue_book_rentals if rental.due_date < (today - datetime.timedelta(weeks=3))]

    return render(request, 'gear/gearmaster.html', {
        'rentals': {
            'current': current_gear_rentals + current_book_rentals,
            'overdue': overdue_gear_rentals + overdue_book_rentals,
            'long': long_gear_rentals + long_book_rentals,
            'all': all_gear_rentals + all_book_rentals
        }
    })

@Execs
def create_rental(request, type):
    if type == "gear":
        form_type = GearRentalForm
    elif type == "book":
        form_type = BookRentalForm
    else:
        raise Http404(f"Rental type '${type}' not recognized")
    
    if request.method == "POST":
        form = form_type(request.POST)
        if form.is_valid():
            rental = form.save(commit=False)
            rental.qm = request.user
            form.save()
            return redirect("rentals")
    else:
        form = form_type()

    return render(request, 'gear/create_rental.html', {
        'form': form,
        'type': type
    })

@Execs
def edit_rental(request, pk, type):
    if type == "gear":
        rental_model = GearRental
        form_type = GearRentalForm
    elif type == "book":
        rental_model = BookRental
        form_type = BookRentalForm
    else:
        raise Http404(f"Rental type '${type}' not recognized")
    
    rental = get_object_or_404(rental_model, pk=pk)

    if request.method == "POST":
        form = form_type(request.POST, instance=rental)
        if form.is_valid():
            form.save()
            return redirect("rentals")
    else:
        form = form_type(instance=rental)

    return render(request, 'gear/edit_rental.html', {
        'form': form,
        'type': type
    })
    


@Execs
def renew_rental(request, pk, type):
    if request.method == "POST":
        rental_type = GearRental if type == "gear" else BookRental
        rental = get_object_or_404(rental_type, pk=pk)
        print(rental)

        rental.due_date += datetime.timedelta(weeks=1)
        rental.extensions += 1
        rental.save()

    return redirect('rentals')

@Execs
def return_rental(request, pk, type):
    if request.method == "POST":
        rental_type = GearRental if type == "gear" else BookRental
        rental = get_object_or_404(rental_type, pk=pk)

        rental.return_date = timezone.localdate()
        rental.save()

    return redirect('rentals')

@Execs
def lost_rental(request, pk, type):
    if request.method == "POST":
        rental_type = GearRental if type == "gear" else BookRental
        rental = get_object_or_404(rental_type, pk=pk)

        rental.lost = True
        rental.save()

    return redirect('rentals')
