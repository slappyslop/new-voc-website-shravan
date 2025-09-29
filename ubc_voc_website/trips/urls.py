from django.urls import path
from .views import *

urlpatterns = [
    path('', trips, name="trips"),
    path('create', trip_create, name="trip_create"),
    path('edit/<int:id>', trip_edit, name="trip_edit"),
    path('delete/<int:id>', trip_delete, name="trip_delete"),
    path('details/<int:id>', trip_details, name="trip_details"),
    path('mark-going/<int:trip_id>/<int:user_id>', mark_as_going, name="mark_as_going"),
    path('my-trips', my_trips, name="my_trips"),
    path('clubroom-calendar', clubroom_calendar, name="clubroom_calendar")
]