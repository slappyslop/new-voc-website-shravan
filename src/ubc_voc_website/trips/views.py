from django.shortcuts import get_object_or_404, render, redirect

from django.contrib.auth.decorators import login_required
from ubc_voc_website.decorators import Admin, Members, Execs

from .models import Trip
from .forms import TripForm, TripSignupForm

import datetime

def trips(request):
    trips = Trip.objects.filter(start_time__gte=datetime.datetime.now(), published=True).order_by('-start_time')
    return render(request, 'trips/trip_agenda.html', {'trips': trips})

@Members
def my_trips(request):
    previous_trips = Trip.objects.filter(start_time__lte=datetime.datetime.now(), organizers=request.user).order_by('-start_time')
    grouped_previous_trips = {}
    for trip in previous_trips:
        month = trip.start_time.strftime('%B %Y')
        if month not in grouped_previous_trips:
            grouped_previous_trips[month] = []
        grouped_previous_trips[month].append(trip)

    upcoming_trips = Trip.objects.filter(start_time__gt=datetime.datetime.now(), organizers=request.user).order_by('-start_time')
    grouped_upcoming_trips = {}
    for trip in upcoming_trips:
        month = trip.start_time.strftime('%B %Y')
        if month not in grouped_upcoming_trips:
            grouped_upcoming_trips[month] = []
        grouped_upcoming_trips[month].append(trip)

    return render(request, 'trips/my_trips.html', {'previous_trips': grouped_previous_trips, 'upcoming_trips': grouped_upcoming_trips})

@Members
def trip_create(request):
    if request.method == "POST":
        form = TripForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('trip_agenda')
    else:
        form = TripForm()
    return render(request, 'trips/trip_form.html', {'form': form})

@Members
def trip_edit(request, id):
    trip = get_object_or_404(Trip, id=id)

    if not trip.organizers.filter(pk=request.user.pk).exists():
        return render(request, 'access_denied.html', status=403)
    else:
        if request.method == "POST":
            form = TripForm(request.POST)
            if form.is_valid():
                form.save(user=request.user)
                return redirect('trip_agenda')
        else:
            form = TripForm(instance=trip)
        return render(request, 'trips/trip_form.html', {'form': form})

@Members
def trip_details(request, id):
    return "<p>placeholder for trip details page"
