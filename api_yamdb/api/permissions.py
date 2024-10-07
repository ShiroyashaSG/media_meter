from rest_framework import permissions


class IsOwnerOrModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешает редактирование и удаление только владельцам,
    модераторам и администраторам.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_moderator
            or request.user.is_admin
            or obj.author == request.user
        )


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


class IsAnonymous(permissions.BasePermission):
    """Разрешение, позволяющее просматривать просматривать
    данные анонимному пользователю.
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class IsAuthor(permissions.BasePermission):
    """Разрешение, позволяющее взаимодействовать с данными автору.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return getattr(obj, 'author', None) == request.user


class IsModerator(permissions.BasePermission):
    """Разрешение, позволяющее взаимодействовать с данными
    модератеру.
    """

    def has_permission(self, request, view):
        # Доступ разрешён только аутентифицированным пользователям с правами суперпользователя, администратора или сотрудника
        return (
            request.user.is_authenticated
            and request.user.is_moderator
        )

    def has_object_permission(self, request, view, obj):
        # Проверка на уровне объекта, что пользователь суперпользователь, администратор или сотрудник
        return self.has_permission(request, view)


class IsSuperUserOrIsAdmin(permissions.BasePermission):
    """Разрешение, дающее полные права для взаимодействия с контентом.
    """

    def has_permission(self, request, view):
        # Доступ разрешён только аутентифицированным пользователям с правами суперпользователя, администратора или сотрудника
        return (
            request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_superuser
                or request.user.is_staff
            )
        )

    def has_object_permission(self, request, view, obj):
        # Проверка на уровне объекта, что пользователь суперпользователь, администратор или сотрудник
        return self.has_permission(request, view)
