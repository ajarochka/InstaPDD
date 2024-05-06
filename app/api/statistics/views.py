from utils.rest import CustomJsonRenderer, CustomDjangoModelPermissions
from django_filters import rest_framework as django_filters
from django.contrib.auth import get_user_model
from . import serializers as stat_serializers
from rest_framework.response import Response
from . import filters as stat_filters
from rest_framework import generics
from django.db.models import Count
from apps.post.models import Post

UserModel = get_user_model()


class CustomerCountReportApi(generics.GenericAPIView):
    serializer_class = stat_serializers.CountSerializer
    permission_classes = (CustomDjangoModelPermissions,)
    renderer_classes = (CustomJsonRenderer,)
    queryset = UserModel.objects.all()
    pagination_class = None

    # @method_decorator(cache_page(settings.CACHE_TTL))
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response({'count': queryset.count()})


class NewCustomerReportApi(generics.GenericAPIView):
    serializer_class = stat_serializers.NewCustomerReportSerializer
    permission_classes = (CustomDjangoModelPermissions,)
    filter_backends = (django_filters.DjangoFilterBackend,)
    renderer_classes = (CustomJsonRenderer,)
    filterset_class = stat_filters.CustomerFilter
    queryset = UserModel.objects.all()
    pagination_class = None

    # @method_decorator(cache_page(settings.CACHE_TTL))
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.values('date_joined__date').annotate(count=Count('id'))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class PostCountReportApi(generics.GenericAPIView):
    serializer_class = stat_serializers.CountSerializer
    permission_classes = (CustomDjangoModelPermissions,)
    renderer_classes = (CustomJsonRenderer,)
    queryset = Post.objects.all()
    pagination_class = None

    # @method_decorator(cache_page(settings.CACHE_TTL))
    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        return Response({'count': queryset.count()})
