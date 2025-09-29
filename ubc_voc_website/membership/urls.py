from django.urls import path
from .views import *

urlpatterns = [ 
    path('join', join, name="join"),
    path('waiver/<int:membership_id>', waiver, name="waiver"),
    path("members", member_list, name="members"),
    path("profile/<int:id>", profile, name="profile"),
    path("edit-profile", edit_profile, name="edit_profile"),
    path("view-waiver/<int:id>", view_waiver, name="view_waiver"),
    path("manage-memberships", manage_memberships, name="manage_memberships"),
    path("toggle/<int:membership_id>", toggle_membership, name="toggle_membership"),
    path("manage-roles", manage_roles, name="manage_roles"),
    path("membership-stats", membership_stats, name="membership_stats"),
    path("download-member-table/<str:type>", download_member_table, name="download_member_table")
]