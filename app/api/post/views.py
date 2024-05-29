from utils.rest import CustomJsonRenderer
from apps.post.choices import PostStatus
from .serializers import PostSerializer
from rest_framework import generics
from apps.post.models import Post


class PostListApiView(generics.ListAPIView):
    queryset = Post.objects.filter(status=PostStatus.APPROVED)
    renderer_classes = (CustomJsonRenderer,)
    serializer_class = PostSerializer
    ordering_fields = ('created_at',)


class PostRetrieveApiView(generics.RetrieveAPIView):
    queryset = Post.objects.filter(status=PostStatus.APPROVED)
    renderer_classes = (CustomJsonRenderer,)
    serializer_class = PostSerializer
