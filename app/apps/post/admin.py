from django.utils.translation import gettext_lazy as _
from .models import Post, PostComment, PostImage
from django.utils.html import format_html
from django.contrib import admin
from .choices import PostStatus

STATUS_ICON_MAP = {
    PostStatus.PENDING: 'icon-alert.svg',
    PostStatus.APPROVED: 'icon-yes.svg',
    PostStatus.REJECTED: 'icon-no.svg',
}


class PostCommentInline(admin.TabularInline):
    model = PostComment
    extra = 0


class PostImageInline(admin.TabularInline):
    model = PostImage
    extra = 0
    readonly_fields = ('get_preview',)

    @admin.display(description=_('Preview'))
    def get_preview(self, obj):
        if not (obj and obj.file):
            return ''
        return format_html(
            f'<a href="javascript:void(0)" class="image-modal-btn">'
            f'<img style="width: 5rem; height: 5rem; object-fit: cover; border-radius: 0.3rem;" src="{obj.file.url}"></img>'
            f'</a>'
        )


class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'category', 'get_status', 'created_at',)
    list_display_links = ('id', 'user',)
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'category__name',)
    list_filter = ('category',)
    inlines = (PostCommentInline, PostImageInline,)

    @admin.display(description=_('Status'))
    def get_status(self, obj):
        return format_html(
            f'<img src="/static/admin/img/{STATUS_ICON_MAP[obj.status]}" alt="True">'
            f'</span>&nbsp;&nbsp;{obj.get_status_display()}'
        )


admin.site.register(Post, PostAdmin)
