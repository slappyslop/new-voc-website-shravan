from django.urls import path
from .views import *

urlpatterns = [
    path('gear-hours/', gear_hours, name="gear_hours"),
    path('rentals/', rentals, name="rentals"),
    path('rentals/create/<str:type>/', create_rental, name="create_rental"),
    path('rentals/edit/<str:type>/<int:pk>/', edit_rental, name="edit_rental"),
    path('rentals/renew/<str:type>/<int:pk>/', renew_rental, name="renew_rental"),
    path('rentals/return/<str:type>/<int:pk>/', return_rental, name="return_rental"),
    path('rentals/mark_lost/<str:type>/<int:pk>/', lost_rental, name="lost_rental")
]
