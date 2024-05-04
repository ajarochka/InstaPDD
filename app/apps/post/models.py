# from django.contrib.gis.db.models import PointField

from utils.common import format_offset
from apps.category.models import Category, Violator

from django.db import models
from django.contrib.auth import get_user_model

# Create your models here.

UserModel = get_user_model()

class Post(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.SET_NULL, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    # location = PointField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'


class PostImage(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='photos/%Y/%m/%d')
    created_at = models.DateTimeField(auto_now_add=True)

class PostComment(models.Model):
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    text = models.TextField()
