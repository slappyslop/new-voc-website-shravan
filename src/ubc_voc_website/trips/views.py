from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from ubc_voc_website.decorators import Admin, Members, Execs
from ubc_voc_website.utils import is_member

from .models import Meeting, Trip, TripSignup, TripSignupTypes
from .forms import TripForm, TripSignupForm

from membership.models import Profile

import datetime
import pytz
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
            form = TripForm(request.POST, instance=trip, user=request.user)
            if form.is_valid():
                form.save(user=request.user)
                return redirect('trips')
            else:
                print(form.errors)
        else:
            form = TripForm(instance=trip, user=request.user)
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
    trip = get_object_or_404(Trip, id=id)
    if request.POST:
        form = TripSignupForm(request.POST, user=request.user, trip=trip)
        if form.is_valid():
            form.save()
        else:
            print(form.errors)

    organizers = Profile.objects.filter(user__in=trip.organizers.all()).values(
        'user__id', 'first_name', 'last_name'
    )
    try:
        description = json.loads(trip.description).get('html', '')
    except json.JSONDecodeError:
        description = trip.description

    if is_member(request.user):
        interested_list, committed_list, going_list = [], [], []
        form = None

        # get existing signups
        if trip.use_signup:
            interested_signups = TripSignup.objects.filter(trip=trip, type=TripSignupTypes.INTERESTED)
            for signup in interested_signups:
                profile = Profile.objects.get(user=signup.user)
                interested_list.append({
                    'name': profile.full_name_with_pronouns,
                    'id': signup.user.id,
                    'signup_answer': signup.signup_answer,
                    'car_spots': signup.car_spots if signup.can_drive else 0
                })
            committed_signups = TripSignup.objects.filter(trip=trip, type=TripSignupTypes.COMMITTED)
            for signup in committed_signups:
                profile = Profile.objects.get(user=signup.user)
                committed_list.append({
                    'name': profile.full_name_with_pronouns,
                    'id': signup.user.id,
                    'signup_answer': signup.signup_answer,
                    'car_spots': signup.car_spots if signup.can_drive else 0
                })
            going_signups = TripSignup.objects.filter(trip=trip, type=TripSignupTypes.GOING)
            for signup in going_signups:
                profile = Profile.objects.get(user=signup.user)
                going_list.append({
                    'name': profile.full_name_with_pronouns,
                    'id': signup.user.id,
                    'signup_answer': signup.signup_answer,
                    'car_spots': signup.car_spots if signup.can_drive else 0
                })

            interested_car_spots = sum(signup['car_spots'] for signup in interested_list)
            committed_car_spots = sum(signup['car_spots'] for signup in committed_list)
            going_car_spots = sum(signup['car_spots'] for signup in going_list)

            # get form for new signups
            if trip.valid_signup_types:
                form = TripSignupForm(user=request.user, trip=trip)

    return render(request, 'trips/trip.html', {
        'trip': trip, 
        'organizers': organizers, 
        'description': description, 
        'signups': {"interested": interested_list, "committed": committed_list, "going": going_list},
        'car_spots': {"interested": interested_car_spots, "committed": committed_car_spots, "going": going_car_spots},
        'form': form
        })

@Members
def clubroom_calendar(request):
    trips_calendar = []

    upcoming_clubroom_events = Trip.objects.filter(in_clubroom=True).values(
        'id', 'name', 'start_time', 'end_time'
    )
    for event in upcoming_clubroom_events:
        trips_calendar.append({
            'id': event.id,
            'title': event.name,
            'start': event.start_time.isoformat(),
            'end': event.end_time.isoformat(),
            'color': '#0000FF'
        })

    upcoming_clubroom_pretrips = Trip.objects.filter(pretrip_location="VOC Clubroom").values(
        'id', 'name', 'pretrip_time'
    )
    for pretrip in upcoming_clubroom_pretrips:
        end_time = pretrip.pretrip_time + datetime.timedelta(hours=1)

        trips_calendar.append({
            'id': pretrip.id, # passing in the trip ID, so clicking the pretrip calendar event will link to trip details page
            'title': f"Pretrip Meeting - {event.name}",
            'start': pretrip.pretrip_time.isoformat(),
            'end': end_time.isoformat(),
            'color': "#00FF00"
        })

    pacific_timezone = pytz.timezone('America/Vancouver')
    meeting_sets = Meeting.objects.all()
    for set in meeting_sets:
        start_time = set.start_date.astimezone(pacific_timezone)
        while start_time.date() <= set.end_date:
            trips_calendar.append({
                'title': set.name,
                'start': start_time.isoformat(),
                'end': (start_time + datetime.timedelta(minutes=set.duration)).isoformat(),
                'color': "#FF0000"
            })
            start_time += datetime.timedelta(days=7)

    # TODO add gear hours in here too

    return render(request, 'trips/clubroom_calendar.html', {
        'trips_calendar': json.dumps(trips_calendar)
    })


