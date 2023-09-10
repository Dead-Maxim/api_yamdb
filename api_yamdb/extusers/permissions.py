from django.contrib.auth import get_user_model
from rest_framework import permissions


User = get_user_model()


class Anonyms(permissions.BasePermission):
    """Аноним

    Проверок нет, почти идентично AllowAny,
    но встроена защита от любой записи (SAFE_METHODS)
    """

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS


class AuthUsers(permissions.BasePermission):
    """Аутентифицированный пользователь (user)

    Прошёл аутентификацию или SAFE_METHODS.
    Для объектов в плюс к авторизованности
    в случае не SAFE_METHODS - И проверка на авторство.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (
                request.user.is_authenticated
                and obj.author == request.user
            )
        )


class AuthUsersHard(permissions.BasePermission):
    """Аутентифицированный пользователь (user)

    Единственная проверка - что прошёл аутентификацию.
    Author-ство объекта и SAFE_METHODS не имеют значения.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated


class Moderators(permissions.BasePermission):
    """Модератор или author объекта

    Проверка - прошёл аутентификацию,
    и юзеру выставлен флаг is_moderator
    (роль мадератор и выше, или он supervisor),
    или author объекта, или SAFE_METHODS.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user: User = request.user

        if not user.is_authenticated:
            return False

        return (
            user.is_moderator()
            or obj.author == user
        )


class ModeratorsHard(permissions.BasePermission):
    """Модератор

    Проверка - прошёл аутентификацию,
    и юзеру выставлен флаг is_moderator
    (роль мадератор и выше, или он supervisor).
    Author-ство объекта и SAFE_METHODS не имеют значения.
    """

    def has_permission(self, request, view):
        user: User = request.user

        if not user.is_authenticated:
            return False

        return user.is_moderator()

    def has_object_permission(self, request, view, obj):
        user: User = request.user

        if not user.is_authenticated:
            return False

        return user.is_moderator()


class Admins(permissions.BasePermission):
    """Администратор или author объекта

    Проверка - прошёл аутентификацию,
    и юзеру выставлен флаг is_admin
    (роль admin, или он supervisor),
    или author объекта, или SAFE_METHODS.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user: User = request.user

        if not user.is_authenticated:
            return False

        return user.is_admin()

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user: User = request.user

        if not user.is_authenticated:
            return False

        return user.is_admin()


class AdminsHard(permissions.BasePermission):
    """Администратор

    Проверка - прошёл аутентификацию,
    и юзеру выставлен флаг is_admin
    (роль admin, или он supervisor).
    Author-ство объекта и SAFE_METHODS не имеют значения.
    """

    def has_permission(self, request, view):
        user: User = request.user

        if not user.is_authenticated:
            return False

        return user.is_admin()

    def has_object_permission(self, request, view, obj):
        user: User = request.user

        if not user.is_authenticated:
            return False

        return user.is_admin()


class Supervisors(permissions.BasePermission):
    """Supervisors

    или author объекта, или SAFE_METHODS.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        user: User = request.user

        if not user.is_authenticated:
            return False

        return user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        user: User = request.user

        if not user.is_authenticated:
            return False

        return user.is_superuser


class SupervisorsHard(permissions.BasePermission):
    """Supervisors

    Author-ство объекта и SAFE_METHODS не имеют значения.
    """

    def has_permission(self, request, view):
        user: User = request.user

        if not user.is_authenticated:
            return False

        return user.is_superuser

    def has_object_permission(self, request, view, obj):
        user: User = request.user

        if not user.is_authenticated:
            return False

        return user.is_superuser
