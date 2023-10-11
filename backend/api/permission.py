from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    '''Полномочия администратора.'''

    def has_object_permission(self, request, view):
        return (request.method in SAFE_METHODS
                or request.user.is_authenticated and request.user.is_superuser)


class IsAuthorOrReadOnly(BasePermission):
    '''Полномочия автора.'''

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user == obj.author)


class IsAdminOrAuthor(BasePermission):
    '''Полномочия администратора и автора.'''

    def has_object_permission(self, request, view, obj):
        return (request.method in SAFE_METHODS
                or request.user == obj.author or request.user.is_superuser)
