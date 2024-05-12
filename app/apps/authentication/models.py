from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token
from django.db import models


class CustomToken(Token):
    expires_at = models.DateTimeField('Expiration date', blank=True, null=True)


class Profile(AbstractUser):
    pass
