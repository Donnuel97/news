from rest_framework import serializers
from .models import News, Tag, Like
from django.contrib.auth.models import User

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"]
        )
        return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']

class NewsSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)  # Use TagSerializer instead of ID list
    likes_count = serializers.SerializerMethodField()  # Calculate likes dynamically
    author = serializers.StringRelatedField(read_only=True)  # Show username instead of ID

    class Meta:
        model = News
        fields = ['id', 'title', 'text', 'picture', 'views', 'likes_count', 'tags', 'created_at', 'author']

    def get_likes_count(self, obj):
        return obj.likes.count()  # Counts the number of likes for the news

    def create(self, validated_data):
        # Get the user from the context (the logged-in user)
        user = self.context['request'].user
        
        # Extract tags from the validated data
        tags_data = validated_data.pop('tags', [])
        
        # Create the news instance and set the author to the logged-in user
        news = News.objects.create(author=user, **validated_data)
        
        # Add tags to the news item
        for tag_data in tags_data:
            tag, created = Tag.objects.get_or_create(name=tag_data['name'])
            news.tags.add(tag)
        
        return news
# class TagSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Tag
#         fields = ['name']

# class NewsSerializer(serializers.ModelSerializer):
#     tags = TagSerializer(many=True)  # ✅ Use TagSerializer instead of ID list
#     likes_count = serializers.SerializerMethodField()  # Calculate likes dynamically

#     class Meta:
#         model = News
#         fields = ['id', 'title', 'text', 'picture', 'views', 'likes_count', 'tags', 'created_at']

#     def get_likes_count(self, obj):
#         return obj.likes.count()  # Counts the number of likes for the news

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
