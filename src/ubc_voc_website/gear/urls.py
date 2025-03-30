from django.urls import path
from .views import *

urlpatterns = [
    path('gear-hours', gear_hours, name="gear_hours"),
]