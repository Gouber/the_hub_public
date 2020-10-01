from rest_framework import permissions

from login_register_service_hub.models import CustomUser


class AnonymousUserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return not request.user.is_authenticated


class StudentUserPermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.usertype == CustomUser.USERTYPE_DICT["STUDENT"]


class StudentWithLeasePermission(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.lease
