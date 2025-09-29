from django.urls import path
from .views import *

urlpatterns = [
    path('user/manage', manage_user_gallery, name="manage_user_gallery"),
    path('user/delete/<int:photo_id>/', delete_user_photo, name="delete_user_photo"),
    path('trip/manage/<int:trip_id>', manage_trip_gallery, name="manage_trip_gallery"),
]