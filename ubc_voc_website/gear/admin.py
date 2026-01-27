from django.contrib import admin

from .models import CancelledGearHour, GearHour, Rental

@admin.register(GearHour)
class GearHourAdmin(admin.ModelAdmin):
    list_display = ("qm_name", "start_date", "end_date", "start_time", "duration")
    search_fields = ("qm_name",)

    def qm_name(self, obj):
        return obj.qm.display_name
    
@admin.register(CancelledGearHour)
class CancelledGearHourAdmin(admin.ModelAdmin):
    list_display = ("qm_name", "date")
    search_fields = ("qm_name",)

    def qm_name(self, obj):
        return obj.gear_hour.qm.display_name

    def date(self, obj):
        return obj.date

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "type", "what", "deposit")
    search_fields = ("member__profile__first_name", "member__profile__last_name", "what")

    def first_name(self, obj):
        return obj.member.profile.first_name
    
    def last_name(self, obj):
        return obj.member.profile.last_name
