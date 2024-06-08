from django.contrib.auth import get_user_model

from apps.post.choices import PostStatus
from utils.common import normalize_phone
from rest_framework import serializers

UserModel = get_user_model()


class CustomerSerializer(serializers.ModelSerializer):
    total_posts = serializers.SerializerMethodField(read_only=True)
    approved_posts = serializers.SerializerMethodField(read_only=True)
    rejected_posts = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserModel
        exclude = ('password',)

    def get_total_posts(self, obj):
        return obj.posts.count()

    def get_approved_posts(self, obj):
        return obj.posts.filter(status=PostStatus.APPROVED).count()

    def get_rejected_posts(self, obj):
        return obj.posts.filter(status=PostStatus.REJECTED).count()
