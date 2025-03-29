import json
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
from rest_framework.renderers import JSONRenderer
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.middleware.csrf import get_token
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.generics import CreateAPIView


class NewsCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        title = request.data.get('title')
        text = request.data.get('text')
        picture = request.data.get('picture')
        tags = request.data.get('tags', "[]")  # Default to empty list
        new_tags = request.data.get('new_tags', '')

        try:
            tags = json.loads(tags) if isinstance(tags, str) else tags  # Convert JSON string to list
        except json.JSONDecodeError:
            return Response({'error': 'Invalid tags format.'}, status=status.HTTP_400_BAD_REQUEST)

        print("Received tag names:", tags)  # Debugging

        # Convert tag names to Tag objects
        tag_objects = []
        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)  # Find or create the tag
            tag_objects.append(tag)

        # Handle new tags
        if new_tags:
            tag_names = [tag.strip() for tag in new_tags.split(',') if tag.strip()]
            for tag_name in tag_names:
                tag, created = Tag.objects.get_or_create(name=tag_name)
                tag_objects.append(tag)

        # Create the news post
        news = News.objects.create(
            title=title,
            text=text,
            picture=picture,
            author=request.user
        )

        # Assign tags
        if tag_objects:
            news.tags.set(tag_objects)  #  Now setting tag objects

        news.save()
        return Response({'message': 'News created successfully', 'news_id': news.id}, status=status.HTTP_201_CREATED)


class TagListView(APIView):
    permission_classes = [AllowAny]  # Allow access to anyone (even unauthenticated)
    
    def get(self, request):
        tags = Tag.objects.all()  # Get all tags from the database
        serializer = TagSerializer(tags, many=True)  # Serialize the tag data
        return Response(serializer.data)  # Return tags as JSON response


def news_by_tag_view(request, tag_name):
    tag = Tag.objects.get(name=tag_name)
    news_list = tag.news.all()
    return render(request, 'news/news_list.html', {'news_list': news_list, 'tag': tag})



def logout_view(request):
    logout(request)
    return redirect('news-list')


    return render(request, 'news/news_detail.html', {'news': news})
class NewsPagination(PageNumberPagination):
    page_size = 3  # Load 3 news items at a time
    page_size_query_param = 'page_size'
    max_page_size = 10

class NewsListView(generics.ListAPIView):
    queryset = News.objects.all().order_by('-created_at')  # Ensure ordering
    serializer_class = NewsSerializer
    pagination_class = NewsPagination
    permission_classes = [AllowAny]  # Allow any user to access the news list

    def get_queryset(self):
        tag_name = self.request.query_params.get('tag', None)
        queryset = News.objects.all().order_by('-created_at')
        if tag_name:
            queryset = queryset.filter(tags__name=tag_name)
        return queryset

class NewsDetailView(generics.RetrieveAPIView):
    queryset = News.objects.all()
    serializer_class = NewsSerializer
    renderer_classes = [JSONRenderer]  #  Forces JSON response
    permission_classes = [AllowAny]  # Allow access to anyone (even unauthenticated)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views += 1
        instance.save()

        serializer = self.get_serializer(instance)
        data = {
            "status": "success",
            "message": "News article retrieved successfully",
            "data": serializer.data,
        }

        return Response(data)  

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
    permission_classes = [IsAuthenticated]  #  Ensure user is logged in

    def delete(self, request, news_id):
        news = get_object_or_404(News, id=news_id)

        # Only allow the author to delete the post
        if request.user != news.author:
            return Response({"error": "You are not allowed to delete this post."}, status=status.HTTP_403_FORBIDDEN)

        news.delete()
        return Response({"message": "News deleted successfully!"}, status=status.HTTP_204_NO_CONTENT)


##APIs

@csrf_exempt
def get_csrf_token(request):
    """Return CSRF token for frontend/API use"""
    return JsonResponse({"csrfToken": get_token(request)})



@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """API for user registration without CSRF issues"""
    username = request.data.get('username')
    email = request.data.get('email')
    password = request.data.get('password')

    if not username or not email or not password:
        return Response({"error": "All fields are required."}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"error": "Username already taken."}, status=400)

    user = User.objects.create_user(username=username, email=email, password=password)
    token, created = Token.objects.get_or_create(user=user)

    return Response({"message": "User registered successfully!", "token": token.key}, status=201)
    

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """API for user login"""
    
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({"error": "Both username and password are required."}, status=400)

    # Authenticate the user
    user = authenticate(username=username, password=password)

    if user is not None:
        # If user exists and credentials are correct
        token, created = Token.objects.get_or_create(user=user)
        return Response({"message": "Login successful!", "token": token.key}, status=200)
    
    return Response({"error": "Invalid username or password."}, status=400)
    

class LogoutAPIView(APIView):
    """Logout user by deleting token"""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.auth.delete()  # Deletes the token
        return Response({"message": "Logged out successfully."}, status=status.HTTP_200_OK)
