from django.contrib import admin

from .models import Category, Genre, Title


class BaseAdmin(admin.ModelAdmin):
    '''Базовая админ модель.'''
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    '''Админ модель произведения'''

    list_display = ('name', 'year', 'category')
    search_fields = ('name',)
    list_filter = ('category', 'year')
    ordering = ('-year',)
    verbose_name = 'Произведение'
    verbose_name_plural = 'Произведения'


@admin.register(Genre)
class GenreAdmin(BaseAdmin):
    '''Админ модель жанра.'''
    verbose_name = 'Жанр'
    verbose_name_plural = 'Жанры'


@admin.register(Category)
class CategoryAdmin(BaseAdmin):
    '''Админ модель категории.'''
    verbose_name = 'Категория'
    verbose_name_plural = 'Категории'
