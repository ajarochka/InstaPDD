from .statistics import urls as statistics_urls
from .authentication import urls as auth_urls
from .customer import urls as customer_urls
from .comment import urls as comment_urls
from django.urls import path, include
from .post import urls as post_urls

app_name = 'api'

urlpatterns = [
    path('statistics/', include(statistics_urls, namespace='statistics')),
    path('customer/', include(customer_urls, namespace='customer')),
    path('comment/', include(comment_urls, namespace='comment')),
    path('auth/', include(auth_urls, namespace='auth')),
    path('post/', include(post_urls, namespace='post')),
]
