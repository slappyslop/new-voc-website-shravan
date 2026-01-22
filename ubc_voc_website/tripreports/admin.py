from django.contrib import admin
from .models import TripReportCategory

@admin.register(TripReportCategory)
class TripReportCategory(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    