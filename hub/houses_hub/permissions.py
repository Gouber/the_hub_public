from rest_framework import permissions

from login_register_service_hub.models import CustomUser


class StudentPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.usertype == CustomUser.USERTYPE_DICT['STUDENT']

