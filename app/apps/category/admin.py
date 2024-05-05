from django.contrib import admin
from .models import *


class ViolatorAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name',)
    search_fields = ('name',)


class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name',)
    list_display_links = ('id', 'name',)
    search_fields = ('name',)


admin.site.register(Violator, ViolatorAdmin)
admin.site.register(Category, CategoryAdmin)
