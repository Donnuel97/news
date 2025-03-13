from django.urls import path
from .views import *

urlpatterns = [
    path('', news_list_view, name='news-list'),
    path('news/<int:news_id>/', news_detail_view, name='news-detail'),
    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('news/upload/', news_create_view, name='news-create'),
    path('news/tag/<str:tag_name>/', news_by_tag_view, name='news-by-tag'),

    path('news/', NewsListView.as_view(), name='api-news-list'),
    path('news/<int:pk>/', NewsDetailView.as_view(), name='api-news-detail'),
    path('news/<int:news_id>/delete/', DeleteNewsView.as_view(), name='delete-news'),
    path('news/<int:news_id>/like/', LikeNewsView.as_view(), name='like-news'),
]
