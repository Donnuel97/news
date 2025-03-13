from rest_framework import serializers
from .models import News, Tag, Like

class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['name']

class NewsSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)  # ✅ Use TagSerializer instead of ID list
    likes_count = serializers.SerializerMethodField()  # Calculate likes dynamically

    class Meta:
        model = News
        fields = ['id', 'title', 'text', 'picture', 'views', 'likes_count', 'tags', 'created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()  # Counts the number of likes for the news

class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Like
        fields = '__all__'
