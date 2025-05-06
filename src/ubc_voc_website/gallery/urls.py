from django.urls import path
from .views import *

urlpatterns = [
    path('user/manage', manage_user_gallery, name="manage_user_gallery"),
]