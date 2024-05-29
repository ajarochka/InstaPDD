from .serializers import PostCommentSerializer
from rest_framework.response import Response
from utils.rest import CustomJsonRenderer
from apps.post.choices import PostStatus
from rest_framework import generics
from apps.post.models import Post


class PostCommentsListApiView(generics.ListAPIView):
    queryset = Post.objects.filter(status=PostStatus.APPROVED)
    renderer_classes = (CustomJsonRenderer,)
    serializer_class = PostCommentSerializer
    ordering_fields = ('created_at',)

    def list(self, request, *args, **kwargs):
        post = self.get_object()
        queryset = post.comments.all().order_by('-created_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
