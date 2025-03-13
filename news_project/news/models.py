from django.db import models
from django.contrib.auth.models import User

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

def get_default_user():
    return User.objects.first().id  # Gets the first user in the database

class News(models.Model):
    title = models.CharField(max_length=255)
    text = models.TextField()
    picture = models.ImageField(upload_to='news_images/', blank=True, null=True)
    tags = models.ManyToManyField(Tag, related_name="news")
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="news_posts", default=get_default_user)  # ✅ FIXED

    def __str__(self):
        return self.title
    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ('user', 'news')

    def __str__(self):
        return f"{self.user.username} liked {self.news.title}"

class NewsView(models.Model):
    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name="news_views")
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('news', 'user')  # Ensures each user can only have one view per news article