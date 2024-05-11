from django.utils.translation import gettext_lazy as _
from django.db import models


class PostStatus(models.IntegerChoices):
    PENDING = 1, _('Pending')
    REJECTED = 2, _('Rejected')
    APPROVED = 3, _('Approved')
