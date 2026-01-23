from django.urls import path
from .views import *

urlpatterns = [
    path('', trips, name="trips"),
    path('create/', trip_create, name="trip_create"),
    path('edit/<int:id>/', trip_edit, name="trip_edit"),
    path('delete/<int:id>/', trip_delete, name="trip_delete"),
    path('details/<int:id>/', trip_details, name="trip_details"),
    path('trip-signup/<int:trip_id>/', trip_signup, name="trip_signup"),
    path('change-signup-type/<int:signup_id>/<int:new_type>', change_signup_type, name="change_signup_type"),
    path('mark-going/<int:trip_id>/<int:user_id>/', mark_as_going, name="mark_as_going"),
    path('download-participant-list/<int:trip_id>/', download_participant_list, name="download_participant_list"),
    path('trip-organizer-message/', trip_organizer_message, name="trip_organizer_message"),
    path('clubroom-calendar/', clubroom_calendar, name="clubroom_calendar")
]