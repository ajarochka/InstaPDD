from django.contrib.auth import get_user_model
from utils.common import normalize_phone
from rest_framework import serializers

UserModel = get_user_model()


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        exclude = ('password',)
