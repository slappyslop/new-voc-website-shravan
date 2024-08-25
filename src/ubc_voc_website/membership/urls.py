from django.urls import path
from .views import *

urlpatterns = [ 
    path('apply', apply, name="apply"),
    path("members", member_list, name="members"),
    path("profile/<int:id>", profile, name="profile"),
    path("my-profile", my_profile, name="my_profile"),
    path("edit-user-profile/<int:id>", edit_user_profile, name="edit_user_profile"),
    path("manage-roles", manage_roles, name="manage_roles"),
    path("membership-stats", membership_stats, name="membership_stats")
]