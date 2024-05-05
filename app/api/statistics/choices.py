from django.utils.translation import gettext_lazy as _
from django.db import models


class PeriodChoice(models.TextChoices):
    DAILY = 'daily', _('Daily')
    HOURLY = 'hourly', _('Hourly')
