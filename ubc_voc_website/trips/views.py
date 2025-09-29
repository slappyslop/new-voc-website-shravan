from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from ubc_voc_website.decorators import Members
from ubc_voc_website.utils import is_member

from .models import Meeting, Trip, TripSignup, TripSignupTypes
from .forms import TripForm, TripSignupForm

from membership.models import Membership, Profile
from gear.models import CancelledGearHour, GearHour

from membership.utils import get_membership_type

import datetime
import pytz
import json

User = get_user_model()

pacific_timezone = pytz.timezone('America/Vancouver')

def trips(request):
    trips = Trip.objects.filter(start_time__gt=datetime.datetime.now(), published=True)
    trips_list = {}
    all_trip_tags = set()
    for trip in trips:
        month = trip.start_time.strftime('%B %Y')
        if month not in trips_list:
            trips_list[month] = []
        trips_list[month].append(trip)
        for tag in trip.tags.all():
            all_trip_tags.add(tag)
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
            'color': trip.tags.all()[0].colour if trip.tags.exists() else '#808080',
            'tags': [tag.name for tag in trip.tags.all()]
        })

    return render(request, 'trips/trip_agenda.html', {
        'all_trip_tags': list(all_trip_tags),
        'trips_list': trips_list, 
        'trips_calendar': json.dumps(trips_calendar)
    })

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
        trip.delete()
        return redirect('trips')

def trip_details(request, id):
    trip = get_object_or_404(Trip, id=id)
    user_can_signup = get_membership_type(request.user) != Membership.MembershipType.INACTIVE_HONOURARY
    if request.POST and user_can_signup:
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

    if request.user.is_authenticated and is_member(request.user):
        form = None

        going_signups = TripSignup.objects.none()
        interested_list, committed_list, going_list = [], [], []
        interested_car_spots, committed_car_spots, going_car_spots = 0, 0, 0

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
            if trip.valid_signup_types and user_can_signup:
                form = TripSignupForm(user=request.user, trip=trip)

        # get photo gallery
        gallery = getattr(trip, 'gallery', None)

        return render(request, 'trips/trip.html', {
            'trip': trip, 
            'organizers': organizers,
            'description': description, 
            'signups': {"interested": interested_list, "committed": committed_list, "going": going_list},
            'is_going': going_signups.filter(user=request.user).exists(),
            'car_spots': {"interested": interested_car_spots, "committed": committed_car_spots, "going": going_car_spots},
            'form': form,
            'user_can_signup': user_can_signup,
            'gallery': gallery
        })
    
    else:
        return render(request, 'trips/trip.html', {
            'trip': trip,
            'organizers': organizers,
            'description': description
        })

@Members
def mark_as_going(request, trip_id, user_id):
    user = User.objects.get(id=user_id)
    trip = Trip.objects.get(id=trip_id)

    if not trip.organizers.filter(pk=request.user.pk).exists():
        return render(request, 'access_denied.html', status=403)
    else:
        # edit existing signup to going if it exists, else create a new one
        trip_signup, created = TripSignup.objects.get_or_create(
            trip=trip,
            user=user,
        )
        trip_signup.type = TripSignupTypes.GOING
        trip_signup.save()

        return redirect(f"/trips/details/{trip_id}")

@Members
def clubroom_calendar(request):
    events_calendar = []

    upcoming_clubroom_events = Trip.objects.filter(in_clubroom=True).values(
        'id', 'name', 'start_time', 'end_time'
    )
    for event in upcoming_clubroom_events:
        events_calendar.append({
            'id': event['id'],
            'title': event['name'],
            'start': event['start_time'].isoformat(),
            'end': event['end_time'].isoformat(),
            'color': '#0000FF'
        })

    upcoming_clubroom_pretrips = Trip.objects.filter(pretrip_location="VOC Clubroom").values(
        'id', 'name', 'pretrip_time'
    )
    for pretrip in upcoming_clubroom_pretrips:
        end_time = pretrip['pretrip_time'] + datetime.timedelta(hours=1)

        events_calendar.append({
            'id': pretrip['id'], # passing in the trip ID, so clicking the pretrip calendar event will link to trip details page
            'title': f"Pretrip Meeting - {pretrip['name']}",
            'start': pretrip['pretrip_time'].isoformat(),
            'end': end_time.isoformat(),
            'color': "#00FF00"
        })

    meeting_sets = Meeting.objects.all()
    for set in meeting_sets:
        start_time = set.start_date.astimezone(pacific_timezone)
        while start_time.date() <= set.end_date:
            events_calendar.append({
                'title': set.name,
                'start': start_time.isoformat(),
                'end': (start_time + datetime.timedelta(minutes=set.duration)).isoformat(),
                'color': "#FF0000"
            })
            start_time += datetime.timedelta(days=7)

    # TODO add gear hours in here too
    gear_hours = GearHour.objects.filter(start_date__lte=datetime.date.today(), end_date__gte=datetime.date.today())
    cancelled_gear_hours = CancelledGearHour.objects.filter(gear_hour__in=gear_hours)

    for gear_hour in gear_hours:
        qm_name = Profile.objects.get(user=gear_hour.qm).first_name

        date = gear_hour.start_date
        while date <= gear_hour.end_date:
            if not cancelled_gear_hours.filter(gear_hour=gear_hour, date=date).exists():
                start_datetime = datetime.datetime.combine(date, gear_hour.start_time)
                start_datetime = pacific_timezone.localize(start_datetime)
                end_datetime = start_datetime + datetime.timedelta(minutes=gear_hour.duration)

                events_calendar.append({
                    'title': f"Gear Hours - {qm_name}",
                    'start': start_datetime.isoformat(),
                    'end': end_datetime.isoformat()
                })
            date = date + datetime.timedelta(days=7)



    return render(request, 'trips/clubroom_calendar.html', {
        'trips_calendar': json.dumps(events_calendar)
    })


