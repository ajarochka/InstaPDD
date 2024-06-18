from django.urls import path
from . import views

app_name = 'comment'

urlpatterns = [
    path('<int:post_pk>/', views.PostCommentsListApiView.as_view(), name='list'),
    path('<int:post_pk>/create/', views.PostCommentCreateApi.as_view(), name='create'),
]
