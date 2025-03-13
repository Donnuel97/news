from django.contrib import admin
from .models import News, Tag, Like

admin.site.register(News)
admin.site.register(Tag)
admin.site.register(Like)
