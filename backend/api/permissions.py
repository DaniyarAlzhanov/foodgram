from rest_framework import permissions


class IsAuthorOrAdmin(permissions.IsAuthenticatedOrReadOnly):
    """
    Кастомный класс разрешений на проверку авторства или роли админа.
    """

    message = 'Данный запрос недоступен для вас.'

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )
