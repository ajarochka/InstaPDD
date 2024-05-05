from .statistics import urls as statistics_urls
# from .category import urls as category_urls
# from .customer import urls as customer_urls
# from .post import urls as post_urls
from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('statistics/', include(statistics_urls, namespace='statistics')),
    # path('category/', include(category_urls, namespace='category')),
    # path('customer/', include(customer_urls, namespace='customer')),
    # path('post/', include(post_urls, namespace='post')),
]
