from django.shortcuts import get_object_or_404, render, redirect

from django.contrib.auth.decorators import login_required
from ubc_voc_website.decorators import Admin, Members, Execs
from ubc_voc_website.utils import is_member

from .models import Trip
from .forms import TripForm, TripSignupForm

from membership.models import Profile

import datetime
import json

def trips(request):
    trips = Trip.objects.filter(start_time__gt=datetime.datetime.now(), published=True)
    trips_list = {}
    for trip in trips:
        month = trip.start_time.strftime('%B %Y')
        if month not in trips_list:
            trips_list[month] = []
        trips_list[month].append(trip)
    trips_list = dict(sorted(trips_list.items(), key=lambda x: datetime.datetime.strptime(x[0], '%B %Y')))

    trips_calendar = []
    for trip in trips:
        if not trip.end_time:
            end_time = trip.start_time.replace(hour=23, minute=59, second=59)
        else:
            end_time = trip.end_time

        trips_calendar.append({
            'id': trip.id,
            'title': trip.name,
            'start': trip.start_time.isoformat(),
            'end': end_time.isoformat(),
            'color': trip.tags.all()[0].colour if trip.tags.exists() else '#808080'
        })

    return render(request, 'trips/trip_agenda.html', {'trips_list': trips_list, 'trips_calendar': json.dumps(trips_calendar)})

@Members
def my_trips(request):
    previous_trips = Trip.objects.filter(start_time__lte=datetime.datetime.now(), organizers=request.user)
    grouped_previous_trips = {}
    for trip in previous_trips:
        month = trip.start_time.strftime('%B %Y')
        if month not in grouped_previous_trips:
            grouped_previous_trips[month] = []
        grouped_previous_trips[month].append(trip)
    # Sort by month in ascending order
    grouped_previous_trips = dict(sorted(grouped_previous_trips.items(), key=lambda x: datetime.datetime.strptime(x[0], '%B %Y')))

    upcoming_trips = Trip.objects.filter(start_time__gt=datetime.datetime.now(), organizers=request.user)
    grouped_upcoming_trips = {}
    for trip in upcoming_trips:
        month = trip.start_time.strftime('%B %Y')
        if month not in grouped_upcoming_trips:
            grouped_upcoming_trips[month] = []
        grouped_upcoming_trips[month].append(trip)
    # Sort by month in ascending order
    grouped_upcoming_trips = dict(sorted(grouped_upcoming_trips.items(), key=lambda x: datetime.datetime.strptime(x[0], '%B %Y')))

    return render(request, 'trips/my_trips.html', {'previous_trips': grouped_previous_trips, 'upcoming_trips': grouped_upcoming_trips})

@Members
def trip_create(request):
    if request.method == "POST":
        form = TripForm(request.POST)
        if form.is_valid():
            form.save(user=request.user)
            return redirect('trips')
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
            form = TripForm(request.POST, instance=trip)
            if form.is_valid():
                form.save(user=request.user)
                return redirect('trips')
            else:
                print(form.errors)
        else:
            form = TripForm(instance=trip)
        return render(request, 'trips/trip_form.html', {'form': form})
    
@Members
def trip_delete(request, id):
    trip = get_object_or_404(Trip, id=id)

    if not trip.organizers.filter(pk=request.user.pk).exists():
        return render(request, 'access_denied.html', status=403)
    else:
        Trip.objects.filter(id=trip.id).delete()
        return redirect('trips')

@login_required
def trip_details(request, id):
    if request.POST:
        form = TripSignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('trips')
        else:
            print(form.errors)
    else:
        trip = get_object_or_404(Trip, id=id)
        organizers = Profile.objects.filter(user__in=trip.organizers.all()).values(
            'user__id', 'first_name', 'last_name'
        )
        try:
            description = json.loads(trip.description).get('html', '')
        except json.JSONDecodeError:
            description = trip.description

        if trip.use_signup and len(trip.valid_signup_types) > 0 and is_member(request.user):
            form = TripSignupForm(trip=trip)
        else:
            form = None

        return render(request, 'trips/trip.html', {'trip': trip, 'organizers': organizers, 'description': description, 'form': form})


