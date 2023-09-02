from django.contrib.auth import get_user_model
from rest_framework import permissions


User = get_user_model()


class Anonyms(permissions.BasePermission):
    """ Аноним

    Проверок нет, почти идентично AllowAny,
    но встроена защита от любой записи (SAFE_METHODS)
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class AuthUsers(permissions.BasePermission):
    """ Аутентифицированный пользователь (user)

    Единственная проверка - что прошёл аутентификацию.
    На SAFE_METHODS проверки нет,
    так как некоторые добавления ему должны быть доступны.
    Для объектов проверка на авторство.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (
                request.method in permissions.SAFE_METHODS
                or obj.author == request.user
            )
        )


class Moderators(permissions.BasePermission):
    """ Модератор (moderator)

    Проверка - прошёл аутентификацию,
    и юзеру выставлена роль moderator и выше,
    или он вообще supervisor, или автор объекта.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        user: User = request.user
        return (
            user.is_superuser
            or 'moderator' == user.role
            or 'admin' == user.role
        )

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        user: User = request.user
        return (
            user.is_superuser
            or 'moderator' == user.role
            or 'admin' == user.role
            or obj.author == request.user
        )


class Admins(permissions.BasePermission):
    """ Администратор (admin)

    Проверка - прошёл аутентификацию,
    и юзеру выставлена роль admin,
    или он вообще supervisor, или автор объекта.
    """

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        user: User = request.user
        return (
            user.is_superuser
            or 'admin' == user.role
        )

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        user: User = request.user
        return (
            user.is_superuser
            or 'admin' == user.role
            or obj.author == request.user
        )


class Supervisors(permissions.BasePermission):
    """Supervisors only"""

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False

        user: User = request.user
        return (
            user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False

        user: User = request.user
        return (
            user.is_superuser
        )
