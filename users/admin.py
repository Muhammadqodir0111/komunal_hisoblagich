from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone', 'role', 'telegram_id', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('username', 'phone', 'telegram_id')

    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha', {'fields': ('role', 'phone', 'telegram_id')}),
    )


admin.site.register(User, CustomUserAdmin)