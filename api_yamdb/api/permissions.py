from rest_framework import permissions


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Разрешает доступ только администраторам, остальные могут только читать.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class IsModeratorOrOwner(permissions.BasePermission):
    """
    Разрешает редактирование и удаление только модераторам и владельцам.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_moderator or obj.author == request.user)


class CanCreateReview(permissions.BasePermission):
    """
    Разрешает создание отзыва только аутентифицированным пользователям.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
