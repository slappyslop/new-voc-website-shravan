from django.contrib import admin

from .models import Rental

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "type", "what", "deposit")
    search_fields = ("member__profile__first_name", "member__profile__last_name", "what")

    def first_name(self, obj):
        return obj.member.profile.first_name
    
    def last_name(self, obj):
        return obj.member.profile.last_name
