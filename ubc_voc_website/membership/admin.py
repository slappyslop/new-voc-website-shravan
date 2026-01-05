from django.contrib import admin
from .models import Exec, Membership, Profile, PSG

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'type')
    search_fields = ('user',)
    list_filter = ('start_date', 'end_date')

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'phone')
    search_fields = ('user__email', 'first_name', 'last_name')
    list_filter = ('first_name', 'last_name')

    formfield_overrides = {
        
    }

@admin.register(Exec)
class ExecAdmin(admin.ModelAdmin):
    list_display = ('user', 'exec_role')
    search_fields = ('user', 'exec_role')
    list_filter = ('user', 'exec_role')

@admin.register(PSG)
class PSGAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user',)
    list_filter = ('user',)