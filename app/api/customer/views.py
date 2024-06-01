from rest_framework import status as http_status, permissions
from apps.authentication.models import CustomToken
from django.contrib.auth import get_user_model
from rest_framework.response import Response
from .serializers import CustomerSerializer
from utils.rest import CustomJsonRenderer
from rest_framework import generics

UserModel = get_user_model()


class CustomerRetrieveApi(generics.RetrieveAPIView):
    renderer_classes = (CustomJsonRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = UserModel.objects.filter(is_active=True)
    serializer_class = CustomerSerializer

    def get_object(self):
        return self.request.user


class DeleteCustomer(generics.DestroyAPIView):
    renderer_classes = (CustomJsonRenderer,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = UserModel.objects.filter(is_active=True)

    def destroy(self, request, *args, **kwargs):
        instance = request.user
        CustomToken.objects.filter(user=instance).delete()
        instance.delete()
        return Response(status=http_status.HTTP_200_OK)
