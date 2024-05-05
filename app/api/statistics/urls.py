from django.urls import path
from . import views

app_name = 'statistics'

urlpatterns = [
    # path('customer-points-earned/', views.TopCustomerEarnedPointsReportApi.as_view(), name='customer_points_earned'),
    # path('customer-points-used/', views.TopCustomerUsedPointsReportApi.as_view(), name='customer_points_used'),
    # path('active-customer/', views.ActiveCustomerReportApi.as_view(), name='active_customer'),
    path('customer-total/', views.CustomerCountReportApi.as_view(), name='customer_total'),
    # path('average-post/', views.AveragePostReportApi.as_view(), name='average_post'),
    path('new-customer/', views.NewCustomerReportApi.as_view(), name='new_customer'),
    # path('post-total/', views.PostCountReportApi.as_view(), name='post_total'),
    # path('point/', views.PointReportApi.as_view(), name='point'),
    # path('post/', views.PostReportApi.as_view(), name='post'),
]
