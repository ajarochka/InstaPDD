from django.contrib.admin.apps import AdminConfig
from django.contrib import admin


class CustomAdminSite(admin.AdminSite):
    site_header = 'IPDD'
    site_title = 'IPDD'


class CustomAdminConfig(AdminConfig):
    default_site = 'dashboard.admin.CustomAdminSite'
