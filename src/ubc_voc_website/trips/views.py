from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from ubc_voc_website.decorators import Admin, Members, Execs

def trip_agenda(request):
    # calendar and list view of all published trips
    pass

@Members
def my_trips(request):
    # base page for all trips, can navigate to create/edit pages from here
    pass

@Members
def create_trip(request):
    pass

@Members
def edit_trip(request):
    pass

@Members
def view_trip(request):
    pass
