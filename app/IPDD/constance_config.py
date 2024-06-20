from django.utils.translation import gettext_lazy as _

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'
CONSTANCE_CONFIG = {
    'TOKEN_TTL': (60 * 60 * 24, _('API authentication token lifetime in seconds.')),
    'MAX_VIDEO_DURATION': (2 * 60, _('Post video max duration in seconds')),
}
