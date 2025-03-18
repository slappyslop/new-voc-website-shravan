from django.urls import path
from .views import *

urlpatterns = [
    path('', trip_reports, name="trip_reports"),
    path('create', create_trip_report, name="create_trip_report"),
    path('edit/<int:id>', edit_trip_report, name="edit_trip_report"),
    path('delete/<int:id>', delete_trip_report, name="delete_trip_report"),
    path('view/<int:id>', view_trip_report, name="view_trip_report"),
    path('my-trip-reports', my_trip_reports, name="my_trip_reports")
]