from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from ubc_voc_website.decorators import Admin, Members, Execs

from .forms import TripForm, TripSignupForm

def trip_agenda(request):
    # calendar and list view of all published trips
    pass

@Members
def my_trips(request):
    # base page for all trips, can navigate to create/edit pages from here
    pass

@Members
def create_trip(request):
    if request.method == "POST":
        form = TripForm(request.POST)
        if form.is_valid():
            trip = form.save()
            return redirect('trips')
    else:
        form = TripForm()
    return render(request, 'trips/create.html', {'form': form})

@Members
def edit_trip(request):
    pass

@Members
def view_trip(request):
    pass
