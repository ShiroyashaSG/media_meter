from django.contrib import admin

from .models import Category, Genre, Title


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    """Админ модель произведения"""
    list_display = ("name", "year", "category")
    search_fields = ("name",)
    list_filter = ("category", "year")
    ordering = ("-year",)


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    """Админ модель жанра."""
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """Админ модель категории."""
    list_display = ("name", "slug")
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
