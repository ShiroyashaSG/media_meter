from django.contrib import admin
from .models import Review, Comment


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'author_id', 'score', 'pub_date')
    search_fields = ('title__name', 'author_id')
    list_filter = ('score', 'pub_date')
    ordering = ['-pub_date']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'review', 'author', 'text', 'pub_date')
    search_fields = ('review__title', 'author__username')
    list_filter = ('pub_date',)
