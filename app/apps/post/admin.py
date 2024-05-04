from django.contrib import admin
from .models import *

# Register your models here.
class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0
    # exclude = ('post',)

class PostAdmin(admin.ModelAdmin):
    inlines = (PostImageInline,)


admin.site.register(Post, PostAdmin)


