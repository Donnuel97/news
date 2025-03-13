from django.shortcuts import get_object_or_404, redirect, render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .models import *
from .serializers import *
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from .forms import *
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.core.files.storage import FileSystemStorage
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated


@login_required
def news_create_view(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save(commit=False)
            news.author = request.user
            news.save()

            # Add selected tags
            form.save_m2m()

            # Handle new tags manually
            new_tags = request.POST.get('new_tags')
            if new_tags:
                tag_names = [tag.strip() for tag in new_tags.split(',')]
                for tag_name in tag_names:
                    tag, created = Tag.objects.get_or_create(name=tag_name)
                    news.tags.add(tag)

            return redirect('news-list')
    else:
        form = NewsForm()

    return render(request, 'news/news_form.html', {'form': form})


def news_by_tag_view(request, tag_name):
    tag = Tag.objects.get(name=tag_name)
    news_list = tag.news.all()
    return render(request, 'news/news_list.html', {'news_list': news_list, 'tag': tag})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('news-list')
    else:
        form = RegisterForm()
    return render(request, 'news/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('news-list')
    else:
        form = AuthenticationForm()
    return render(request, 'news/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('news-list')
def news_list_view(request):
    return render(request, 'news/news_list.html')

def news_detail_view(request, news_id):
    news = get_object_or_404(News, id=news_id)

    # Check if the user has already viewed the news
    if request.user.is_authenticated:
        view_exists = NewsView.objects.filter(news=news, user=request.user).exists()
        if not view_exists:
            NewsView.objects.create(news=news, user=request.user)
            news.views += 1
            news.save()

    return render(request, 'news/news_detail.html', {'news': news})
class NewsPagination(PageNumberPagination):
    page_size = 3  # Load 3 news items at a time
    page_size_query_param = 'page_size'
    max_page_size = 10

class NewsListView(generics.ListAPIView):
    queryset = News.objects.all().order_by('-created_at')  # ✅ Ensure ordering
    serializer_class = NewsSerializer
    pagination_class = NewsPagination

    def get_queryset(self):
        tag_name = self.request.query_params.get('tag', None)
        queryset = News.objects.all().order_by('-created_at')
        if tag_name:
            queryset = queryset.filter(tags__name=tag_name)
        return queryset


class NewsDetailView(generics.RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# Like/Unlike News
class LikeNewsView(APIView):
    permission_classes = [IsAuthenticated]  # Ensure only logged-in users can like

    def post(self, request, news_id):
        news = get_object_or_404(News, id=news_id)
        user = request.user

        # Like or Unlike Logic
        like, created = Like.objects.get_or_create(user=user, news=news)
        if not created:
            like.delete()
            return Response({"message": "Like removed", "likes_count": news.likes.count()}, status=status.HTTP_200_OK)

        return Response({"message": "Liked", "likes_count": news.likes.count()}, status=status.HTTP_201_CREATED)
    

class DeleteNewsView(generics.DestroyAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    permission_classes = [IsAuthenticated]  # ✅ Ensure user is logged in

    def delete(self, request, news_id):
        news = get_object_or_404(News, id=news_id)

        # ✅ Only allow the author to delete the post
        if request.user != news.author:
            return Response({"error": "You are not allowed to delete this post."}, status=status.HTTP_403_FORBIDDEN)

        news.delete()
        return Response({"message": "News deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)
