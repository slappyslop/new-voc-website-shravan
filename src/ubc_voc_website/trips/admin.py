from django.contrib import admin
from .models import Meeting, Trip, TripTag

@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_time', 'end_time')
    search_fields = ('name',)
    list_filter = ('start_time', 'end_time')

@admin.register(TripTag)
class TripTagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'duration')
    search_fields = ('name',)
