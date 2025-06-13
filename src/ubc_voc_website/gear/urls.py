from django.urls import path
from .views import *

urlpatterns = [
    path('gear-hours/', gear_hours, name="gear_hours"),
    path('gear-hours/delete/<int:id>', delete_gear_hour, name="delete_gear_hour"),
    path('rentals', rentals, name="rentals"),
    path('rentals/create/<str:type>', create_rental, name="create_rental")
]
