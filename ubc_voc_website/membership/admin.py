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
    list_display = ('user', 'first_name', 'last_name', 'exec_role')
    autocomplete_fields = ('user',)
    search_fields = ('user__email', 'user__profile__first_name', 'user__profile__last_name', 'exec_role')

    def first_name(self, obj):
        return obj.user.profile.first_name

    def last_name(self, obj):
        return obj.user.profile.last_name

@admin.register(PSG)
class PSGAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name')
    autocomplete_fields = ('user',)
    search_fields = ('user__email', 'user__profile__first_name', 'user__profile__last_name')

    def first_name(self, obj):
        return obj.user.profile.first_name

    def last_name(self, obj):
        return obj.user.profile.last_name