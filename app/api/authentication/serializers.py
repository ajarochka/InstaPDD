from django.contrib.auth import get_user_model
from utils.common import normalize_phone
from rest_framework import serializers
from .exceptions import WrongPassword

UserModel = get_user_model()


class RegisterCustomerSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password1 = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)
    email = serializers.EmailField(required=False)
    phone = serializers.CharField(required=False)

    def validate(self, attrs):
        if 'phone' in attrs:
            attrs['phone'] = normalize_phone(attrs['phone'])
        if attrs['password1'] != attrs['password2']:
            raise WrongPassword
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=100, required=True)
    new_password = serializers.CharField(max_length=100, required=True)
    new_password1 = serializers.CharField(max_length=100, required=True)
