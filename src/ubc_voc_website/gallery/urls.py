from django.urls import path
from .views import *

urlpatterns = [
    path('create-user-gallery', create_user_gallery, name="create_user_gallery"),
]