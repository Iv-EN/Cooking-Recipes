from django.core.handlers.wsgi import WSGIRequest
from django.db.models import Model
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.routers import APIRootView


class ActivePermission(BasePermission):
    '''Базовые разрешения с проверкой пользователь активен или забанен.'''

    def has_permission(self, request: WSGIRequest, view: APIRootView) -> bool:
        return bool(
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
        )


class AuthorOrReadOnly(ActivePermission):
    '''Права доступа для автора.'''

    def has_object_permission(
            self, request: WSGIRequest, view: APIRootView, obj: Model) -> bool:
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.author
        )


class AdminOrReadOnly(ActivePermission):
    '''Права доступа для админов.'''

    def has_object_permission(
            self, request: WSGIRequest, view: APIRootView
    ) -> bool:
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user.is_staff
        )


class AuthorOrAdmin(ActivePermission):
    '''Права досступа для авторв и админа.'''

    def has_object_permission(
            self, request: WSGIRequest, view: APIRootView, obj: Model
    ) -> bool:
        return (
            request.method in SAFE_METHODS
            or request.user.is_authenticated
            and request.user.is_active
            and request.user == obj.author
            or request.user.is_staff
        )
