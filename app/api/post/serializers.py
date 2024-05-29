from django.utils.formats import date_format
from rest_framework import serializers
from apps.post.models import Post


class PostSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    user_name = serializers.CharField(source='user.username', read_only=True)
    status_name = serializers.SerializerMethodField(read_only=True)
    images = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Post
        exclude = ()

    def get_status_name(self, obj):
        return obj.get_status_display()

    def get_images(self, obj):
        request = self.context.get('request')
        return [request.build_absolute_uri(image.file.url) for image in obj.postimage_set.all()]

    def get_created_at(self, obj):
        return date_format(obj.created_at, format='j E Y, H:i', use_l10n=True)
