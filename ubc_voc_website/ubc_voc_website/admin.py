from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from allauth.account.models import EmailAddress

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

    def save_model(self, request, obj, form, change):
        new_email = request.POST.get('email', '').lower().strip()
        old_email = User.objects.get(pk=obj.pk).email if change else None
        
        if new_email and new_email != old_email:
            User.objects.filter(pk=obj.pk).update(email=new_email)
            EmailAddress.objects.filter(user=obj, primary=True).update(email=new_email)
            self.message_user(request, f'Email updated to {new_email}', level=messages.SUCCESS)
        else:
            super().save_model(request, obj, form, change)
