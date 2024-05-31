from django.urls import path
from . import views

app_name = 'auth'

urlpatterns = [
    path('register/', views.RegisterCustomer.as_view(), name='register'),
    path('login/', views.CustomObtainTokenView.as_view(), name='login'),
    path('logout/', views.Logout.as_view(), name='logout'),
    path('change-password/', views.ChangePasswordApi.as_view(), name='change_password'),
]
