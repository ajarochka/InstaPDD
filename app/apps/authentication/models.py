from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token
from django.db import models


class CustomToken(Token):
    expires_at = models.DateTimeField(_('Expiration date'), blank=True, null=True)


class Profile(AbstractUser):
    phone = models.CharField(_('Phone'), max_length=32, blank=True, null=True)


class BotAdmin(models.Model):
    name = models.CharField(_('Name'), max_length=64)
    tg_id = models.PositiveIntegerField(_('Telegram bot admin'))
    active = models.BooleanField(_('Active'), default=True)
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
