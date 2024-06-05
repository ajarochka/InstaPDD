from django.contrib.auth import get_user_model
from utils.common import normalize_phone
from rest_framework import serializers

UserModel = get_user_model()


class RegisterCustomerSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password1 = serializers.CharField(required=True)
    password2 = serializers.CharField(required=True)
    email = serializers.EmailField()
    phone = serializers.CharField()

    def validate(self, attrs):
        if 'phone' in attrs:
            attrs['phone'] = normalize_phone(attrs['phone'])
        return attrs


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=100, required=True)
    new_password = serializers.CharField(max_length=100, required=True)
    new_password1 = serializers.CharField(max_length=100, required=True)