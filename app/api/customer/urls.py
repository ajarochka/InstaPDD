from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('me/', views.CustomerRetrieveApi.as_view(), name='retrieve'),
]
