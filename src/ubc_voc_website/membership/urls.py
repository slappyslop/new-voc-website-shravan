from django.urls import path
from .views import *

urlpatterns = [ 
    path('join', join, name="join"),
    path('waiver/<int:membership_id>', waiver, name="waiver"),
    path("members", member_list, name="members"),
    path("profile/<int:id>", profile, name="profile"),
    path("edit-profile", edit_profile, name="edit_profile"),
    path("manage-roles", manage_roles, name="manage_roles"),
    path("membership-stats", membership_stats, name="membership_stats")
]