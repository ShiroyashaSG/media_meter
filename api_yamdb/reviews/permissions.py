from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение, которое позволяет редактировать объект только его автору.
    Для безопасных методов (GET, HEAD, OPTIONS) доступ открыт для всех.
    Для небезопасных методов (POST, PUT, PATCH, DELETE) доступ открыт только автору.
    """

    def has_permission(self, request, view):
        # Разрешить доступ для всех аутентифицированных пользователей или безопасные методы
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        # Разрешить безопасные методы (GET, HEAD, OPTIONS) для всех
        if request.method in permissions.SAFE_METHODS:
            return True

        # Разрешить изменение и удаление только автору объекта
        return obj.author == request.user
