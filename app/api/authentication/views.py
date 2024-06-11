from rest_framework import status as http_status, permissions
from rest_framework.authtoken.views import ObtainAuthToken
from .exceptions import WrongPassword, UsernameAlreadyUsed
from apps.authentication.models import CustomToken
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from utils.rest import CustomJsonRenderer
from rest_framework import generics
from django.utils import timezone
from datetime import timedelta
from constance import config
from . import serializers

UserModel = get_user_model()


class RegisterApi(generics.CreateAPIView):
    serializer_class = serializers.RegisterCustomerSerializer
    renderer_classes = (CustomJsonRenderer,)
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        username = data.get('username')
        user, created = UserModel.objects.get_or_create(username=username)
        if not created:
            raise UsernameAlreadyUsed
        user.set_password(data['password1'])
        token = CustomToken.objects.create(user=user)
        token.expires_at = timezone.now() + timedelta(seconds=config.TOKEN_TTL)
        token.save(update_fields=('expires_at',))
        headers = self.get_success_headers(serializer.data)
        res = serializer.data
        res.update({'token': token.key, 'expires_at': token.expires_at})
        return Response(data=res, status=http_status.HTTP_200_OK, headers=headers)


class CustomObtainTokenView(ObtainAuthToken):
    renderer_classes = (CustomJsonRenderer,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        CustomToken.objects.filter(user=user).delete()
        token = CustomToken.objects.create(user=user)
        token.expires_at = timezone.now() + timedelta(seconds=config.TOKEN_TTL)
        token.save(update_fields=('expires_at',))
        return Response({'token': token.key, 'expires_at': token.expires_at})


class ChangePasswordApi(generics.CreateAPIView):
    serializer_class = serializers.ChangePasswordSerializer
    permission_classes = (permissions.IsAuthenticated,)
    renderer_classes = (CustomJsonRenderer,)

    def get_object(self, queryset=None):
        return self.request.user

    def create(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not user.check_password(serializer.data.get('old_password')) \
                or serializer.data.get('new_password') != serializer.data.get('new_password1'):
            raise WrongPassword
        user.set_password(serializer.data.get('new_password'))
        user.save(update_fields=('password',))
        return Response()


class LogoutApi(generics.GenericAPIView):
    renderer_classes = (CustomJsonRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None

    def get(self, request):
        request.user.auth_token.delete()
        return Response(status=http_status.HTTP_200_OK)

# TODO: Move to customer api later.
# class DeleteCustomer(generics.DestroyAPIView):
#     renderer_classes = (CustomJsonRenderer,)
#     permission_classes = (permissions.IsAuthenticated,)
#     queryset = UserModel.objects.filter(is_active=True)
#
#     def destroy(self, request, *args, **kwargs):
#         instance = request.user
#         CustomToken.objects.filter(user=instance).delete()
#         instance.delete()
#         return Response(status=http_status.HTTP_200_OK)
