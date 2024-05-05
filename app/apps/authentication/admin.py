from django.contrib.auth.models import Permission
from django.contrib.auth.admin import UserAdmin
from django.contrib import admin
from .models import *


class ProfileAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'first_name', 'is_active', 'is_staff', 'is_superuser',)
    list_display_links = ('id', 'username', 'email', 'first_name',)
    search_fields = ('username', 'first_name', 'last_name',)
    list_filter = ('is_staff', 'is_superuser', 'is_active',)


class PermissionAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'codename', 'content_type')
    list_display_links = ('id', 'name', 'codename')
    search_fields = ('name', 'codename')
    ordering = ('name',)


admin.site.register(Profile, ProfileAdmin)
admin.site.register(Permission, PermissionAdmin)
