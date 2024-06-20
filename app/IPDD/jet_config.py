from django.utils.translation import gettext_lazy as _

menu_items = [
    {'label': '', 'items': [
        {'name': 'post.post', 'label': _('Posts'), 'permissions': ['post.view_post', ], },
        {'name': 'category.violator', 'label': _('Violators'), 'permissions': ['category.view_violator', ], },
        {'name': 'category.category', 'label': _('Categories'), 'permissions': ['category.view_category', ], },
    ]},
    {'label': _('Authentication'), 'items': [
        {'name': 'authentication.profile', 'label': _('Users'), 'permissions': ['authentication.view_profile', ], },
        {'name': 'auth.group', 'label': _('Groups'), 'permissions': ['auth.view_group'], },
        {'name': 'auth.permission', 'label': _('Permissions'), 'permissions': ['auth.view_permission', ], },
    ]},
    {'label': _('Settings'), 'items': [
        {'name': 'constance.config', 'label': _('Config'), 'permissions': ['constance.view_config', ], },
    ]},
    {'label': _('Periodic Tasks'), 'permissions': ['django_celery_beat.view_periodictask', ], 'items': [
        {'name': 'django_celery_beat.crontabschedule', 'label': _('Crontabs'),
         'permissions': ['django_celery_beat.view_crontabschedule', ], },
        {'name': 'django_celery_beat.periodictask', 'label': _('Periodic tasks'),
         'permissions': ['django_celery_beat.view_periodictask', ], },
    ]},
    {'label': _('API docs'), 'items': [
        {'label': _('Swagger'), 'url': '/swagger/', 'url_blank': True},
        {'label': _('Redoc'), 'url': '/redoc/', 'url_blank': True},
    ]}
]

themes = [
    {
        'theme': 'default',
        'color': '#47bac1',
        'title': 'Default'
    },
    {
        'theme': 'green',
        'color': '#44b78b',
        'title': 'Green'
    },
    {
        'theme': 'light-green',
        'color': '#2faa60',
        'title': 'Light Green'
    },
    {
        'theme': 'light-violet',
        'color': '#a464c4',
        'title': 'Light Violet'
    },
    {
        'theme': 'light-blue',
        'color': '#5EADDE',
        'title': 'Light Blue'
    },
    {
        'theme': 'light-gray',
        'color': '#222',
        'title': 'Light Gray'
    }
]
