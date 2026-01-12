from django.urls import path
from .views import *

urlpatterns = [
    path('rentals/', rentals, name="rentals"),
    path('rentals/create/', create_rental, name="create_rental"),
    path('rentals/edit/<int:id>/', edit_rental, name="edit_rental"),
    path('rentals/renew/<int:id>/', renew_rental, name="renew_rental"),
    path('rentals/return/<int:id>/', return_rental, name="return_rental"),
    path('rentals/mark_lost/<int:id>/', lost_rental, name="lost_rental")
]
