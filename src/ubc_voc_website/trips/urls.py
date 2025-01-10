from django.urls import path
from .views import *

urlpatterns = [
    path('', trips, name="trips"),
    path('create', trip_create, name="trip_create"),
    path('edit/<int:id>', trip_edit, name="trip_edit"),
    path('details/<int:id>', trip_details, name="trip_details"),
    path('my-trips', my_trips, name="my_trips")
]