from django.contrib.auth import get_user_model
from apps.core.fields import OSMPointField
from apps.category.models import Category
from .choices import PostStatus
from django.db import models

UserModel = get_user_model()


class Post(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, related_name='posts', null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    status = models.PositiveSmallIntegerField(choices=PostStatus.choices, default=PostStatus.PENDING)
    address = models.CharField(max_length=128, blank=True, null=True)
    license_plate = models.CharField(max_length=16, blank=True, null=True)
    description = models.TextField(max_length=820)
    location = OSMPointField(blank=True, null=True)
    location_image = models.ImageField(upload_to='photos/%Y/%m/%d', blank=True, null=True)
    active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='photos/%Y/%m/%d')
    file_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)


class PostComment(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.user} - {self.created_at}'
