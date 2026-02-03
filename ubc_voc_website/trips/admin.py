from django.contrib import admin
from .models import Meeting, Trip, TripSignup, TripTag

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')
    search_fields = ('name',)
    list_filter = ('start_time', 'end_time')
    readonly_fields = ('organizers',)

@admin.register(TripSignup)
class TripSignupAdmin(admin.ModelAdmin):
    list_display = ('trip__name', 'user__email', 'type')
    search_fields = ('trip__name', "user__email")
    readonly_fields = ('trip', 'user')

@admin.register(TripTag)
class TripTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'duration')
    search_fields = ('name',)
