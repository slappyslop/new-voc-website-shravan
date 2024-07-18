from django.urls import path
from .views import *

urlpatterns = [ 
    path("member-list", member_list, name="member_list"),
    path("profile/", profile, name="profile"),
    path("my-profile", my_profile, name="my_profile"),
    path("edit-user", edit_user_profile, name="edit_user"),
    path("manage-roles", manage_roles, name="manage_roles"),
    path("membership-stats", member_list, name="membership_stats")
]