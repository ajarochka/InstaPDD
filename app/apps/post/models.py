from django.utils.translation import gettext_lazy as _
from .choices import PostStatus, PostMediaType
from django.contrib.auth import get_user_model
from apps.core.fields import OSMPointField
from apps.category.models import Category
from django.db import models

UserModel = get_user_model()


class Post(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, related_name='posts', verbose_name=_('User'), null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, verbose_name=_('Category'), null=True)
    status = models.PositiveSmallIntegerField(_('Status'), choices=PostStatus.choices, default=PostStatus.PENDING)
    address = models.CharField(_('Address'), max_length=128, blank=True, null=True)
    license_plate = models.CharField(_('License plate'), max_length=16, blank=True, null=True)
    description = models.TextField(_('Description'), max_length=820)
    location = OSMPointField(_('Location'), blank=True, null=True)
    location_image = models.ImageField(_('Location image'), upload_to='photos/%Y/%m/%d', blank=True, null=True)
    active = models.BooleanField(_('Active'), default=False)
    bot_message_id = models.CharField(_('Telegram bot message id'), max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'


class PostMedia(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, verbose_name=_('Post'))
    file = models.FileField(_('File'), upload_to='photos/%Y/%m/%d')
    file_id = models.CharField(_('Telegram bot file id'), max_length=255, blank=True, null=True)
    file_type = models.CharField(_('Type'), max_length=24, choices=PostMediaType.choices, default=PostMediaType.IMAGE)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)


class PostComment(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE, verbose_name=_('User'))
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name=_('Post'))
    text = models.TextField(_('Text'), max_length=500)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user} - {self.created_at}'
