from django.db.models.signals import pre_delete
from django.dispatch import receiver
from .models import PostImage
import os


@receiver(pre_delete, sender=PostImage)
def post_image_pre_delete(sender, instance, **kwargs):
    if not instance.file:
        return
    if os.path.exists(instance.file.path):
        os.remove(instance.file.path)
