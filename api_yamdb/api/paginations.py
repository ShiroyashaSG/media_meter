from rest_framework.pagination import PageNumberPagination


class GenrePagination(PageNumberPagination):
    """Пагинация для Жанров."""

    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 10


class CategoryPagination(PageNumberPagination):
    """Пагинация для Категорий."""

    page_size = 1
    page_size_query_param = 'page_size'
