from django.contrib import admin
from .models import Membership, Profile

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'type')
    search_fields = ('user',)
    list_filter = ('start_date', 'end_date')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'phone')
    search_fields = ('user',)
    list_filter = ('first_name', 'last_name')