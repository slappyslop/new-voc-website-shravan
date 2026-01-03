from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model

User = get_user_model()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ("email", "is_staff", "is_active", "old_id")
    list_filter = ("is_staff", "is_active", "is_superuser")

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (('Important dates'), {'fields': ('last_login',)}),
    )

    search_fields = ('email', 'old_id')
    ordering = ('email',)
