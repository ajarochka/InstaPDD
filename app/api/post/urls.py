from django.urls import path
from . import views

app_name = 'post'

urlpatterns = [
    path('', views.PostListApiView.as_view(), name='list'),
    path('<int:pk>/', views.PostRetrieveApiView.as_view(), name='retrieve'),
]
