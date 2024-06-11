from rest_framework import status as http_status
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
    lookup_field = 'pk'
    lookup_url_kwarg = 'post_pk'

    def list(self, request, *args, **kwargs):
        post = self.get_object()
        queryset = post.comments.all().order_by('-created_at')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PostCommentCreateApi(generics.CreateAPIView):
    renderer_classes = (CustomJsonRenderer,)
    serializer_class = PostCommentSerializer
    queryset = Post.objects.filter(status=PostStatus.APPROVED)
    lookup_field = 'pk'
    lookup_url_kwarg = 'post_pk'

    def create(self, request, *args, **kwargs):
        post = self.get_object()
        user = self.request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=user, post=post)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=http_status.HTTP_200_OK, headers=headers)
