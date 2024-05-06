from django.utils.translation import gettext_lazy as _
from django.db import models


class PostStatus(models.IntegerChoices):
    PENDING = 1, _('Pending')
    APPROVED = 2, _('Approved')
    REJECTED = 3, _('Rejected')
