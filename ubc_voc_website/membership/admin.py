from django.contrib import admin
from .models import Membership

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'type')
    search_fields = ('user',)
    list_filter = ('start_date', 'end_date')