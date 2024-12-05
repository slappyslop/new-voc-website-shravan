from django.urls import path
from .views import *

urlpatterns = [
    path('create', create_trip, name="create_trip")
]