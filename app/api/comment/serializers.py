from django.utils.formats import date_format
from apps.post.models import PostComment
from rest_framework import serializers


class PostCommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = PostComment
        exclude = ()
        read_only_fields = ('post', 'user')

    def get_created_at(self, obj):
        return date_format(obj.created_at, format='j E Y, H:i', use_l10n=True)
