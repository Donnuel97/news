from django.urls import path
from .views import *

urlpatterns = [
    
    path('news/tag/<str:tag_name>/', news_by_tag_view, name='news-by-tag'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('news/create/', NewsCreateView.as_view(), name='news-create'),
    path('news/', NewsListView.as_view(), name='api-news-list'),
    path('news/<int:pk>/', NewsDetailView.as_view(), name='api-news-detail'),
    path('news/<int:news_id>/like/', LikeNewsView.as_view(), name="like-news"),
    path('news/<int:news_id>/delete/', DeleteNewsView.as_view(), name="delete-news"),
    path("api/register/", register_view, name="api-register"),
    path('api/login/', login_view, name='login'),
    path('api/logout/', LogoutAPIView.as_view(), name='logout'),
    path("api/csrf/", get_csrf_token, name="api-csrf"),
    path('tags/', TagListView.as_view(), name='tags-list'),  #
]
