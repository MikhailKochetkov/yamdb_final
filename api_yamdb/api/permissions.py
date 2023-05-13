from rest_framework import permissions


class AuthorOrStuffOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = request.user
        return (obj.author == user
                or request.method in permissions.SAFE_METHODS
                or (not user.is_anonymous
                    and (user.is_moderator or user.is_admin)
                    )
                )


class AdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return (request.method in permissions.SAFE_METHODS
                or (not user.is_anonymous and user.is_admin))


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        return not user.is_anonymous and user.is_admin
