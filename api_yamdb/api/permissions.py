from rest_framework import permissions


class IsOwnerOrModeratorOrAdmin(permissions.BasePermission):
    """
    Класс разрешений, позволяющий редактировать и удалять только владельцам,
    модераторам и администраторам.

    Методы:
        has_object_permission(request, view, obj):
            Проверяет, имеет ли пользователь разрешение на редактирование или
            удаление объекта.
    """
    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь разрешение на редактирование или
        удаление объекта.

        Аргументы:
            request: Объект запроса.
            view: Представление, к которому осуществляется доступ.
            obj: Объект, к которому осуществляется доступ.

        Возвращает:
            bool: True, если пользователь является владельцем, модератором или
            администратором; иначе False.
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
    Класс разрешений, позволяющий доступ только администраторам,
    в то время как остальные могут только читать.

    Методы:
        has_permission(request, view):
            Проверяет, имеет ли пользователь разрешение на выполнение запроса.
    """
    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь разрешение на выполнение запроса.
        
        Аргументы:
            request: Объект запроса.
            view: Представление, к которому осуществляется доступ.

        Возвращает:
            bool: True, если пользователь является администратором или запрос
            безопасный; иначе False.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin


class IsModeratorOrOwner(permissions.BasePermission):
    """
    Класс разрешений, позволяющий редактировать и удалять только модераторам
    и владельцам.

    Методы:
        has_object_permission(request, view, obj):
            Проверяет, имеет ли пользователь разрешение на редактирование или
            удаление объекта.
    """
    def has_object_permission(self, request, view, obj):
        """
        Проверяет, имеет ли пользователь разрешение на редактирование или
        удаление объекта.

        Аргументы:
            request: Объект запроса.
            view: Представление, к которому осуществляется доступ.
            obj: Объект, к которому осуществляется доступ.

        Возвращает:
            bool: True, если пользователь является модератором или владельцем;
            иначе False.
        """
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.is_moderator or obj.author == request.user)


class CanCreateReview(permissions.BasePermission):
    """
    Класс разрешений, позволяющий создание отзыва только аутентифицированным
    пользователям.

    Методы:
        has_permission(request, view):
            Проверяет, имеет ли пользователь разрешение на создание отзыва.
    """
    def has_permission(self, request, view):
        """
        Проверяет, имеет ли пользователь разрешение на создание отзыва.

        Аргументы:
            request: Объект запроса.
            view: Представление, к которому осуществляется доступ.

        Возвращает:
            bool: True, если пользователь аутентифицирован; иначе False.
        """
        return request.user.is_authenticated


class IsAnonymous(permissions.BasePermission):
    """Разрешение, позволяющее просматривать
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
        return (
            request.user.is_authenticated
            and request.user.is_moderator
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsSuperUserOrIsAdmin(permissions.BasePermission):
    """Разрешение, дающее полные права для взаимодействия с контентом.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (
                request.user.is_admin
                or request.user.is_superuser
                or request.user.is_staff
            )
        )

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
