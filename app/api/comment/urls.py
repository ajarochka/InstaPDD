from django.urls import path
from . import views

app_name = 'comment'

urlpatterns = [
    path('<int:pk>/', views.PostCommentsListApiView.as_view(), name='list'),
]
