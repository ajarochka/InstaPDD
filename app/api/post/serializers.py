from django.utils.formats import date_format
from rest_framework import serializers
from apps.post.models import Post


class PostSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    status_name = serializers.SerializerMethodField(read_only=True)
    location = serializers.SerializerMethodField(read_only=True)
    media = serializers.SerializerMethodField(read_only=True)
    comments_count = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        exclude = ()

    def get_status_name(self, obj):
        return obj.get_status_display()

    def get_location(self, obj):
        if not obj.location:
            return None
        lon, lat = obj.location.coords
        return {'latitude': lat, 'longitude': lon}

    def get_media(self, obj):
        request = self.context.get('request')
        return [request.build_absolute_uri(m.file.url) for m in obj.media.all()]

    def get_comments_count(self, obj):
        return obj.comments.count()

    def get_created_at(self, obj):
        return date_format(obj.created_at, format='j E Y, H:i', use_l10n=True)
