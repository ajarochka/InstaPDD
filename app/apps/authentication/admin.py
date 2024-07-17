from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import Permission
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import *


class ProfileAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'is_active', 'is_staff', 'is_superuser',)
    list_display_links = ('id', 'username', 'email', 'first_name',)
    search_fields = ('username', 'first_name', 'last_name',)
    list_filter = ('is_staff', 'is_superuser', 'is_active',)
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'tg_id')}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'groups',
                    'user_permissions',
                ),
            },
        ),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'codename', 'content_type')
    list_display_links = ('id', 'name', 'codename')
    search_fields = ('name', 'codename')
    ordering = ('name',)


class BotAdminAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tg_id', 'created_at')
    list_display_links = ('id', 'name', 'tg_id')
    search_fields = ('name', 'tg_id')
    ordering = ('-created_at',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(BotAdmin, BotAdminAdmin)
admin.site.register(Permission, PermissionAdmin)
