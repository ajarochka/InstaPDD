from django.utils.formats import date_format
from apps.post.models import PostComment
from rest_framework import serializers


class PostCommentSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PostComment
        exclude = ()

    def get_created_at(self, obj):
        return date_format(obj.created_at, format='j E Y, H:i', use_l10n=True)
