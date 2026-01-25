from django.urls import path
from .views import *

urlpatterns = [ 
    path("verify/", membership_verification, name="membership_verification"),
]