from django.urls import Resolver404
from .models import CustomUser

# NOTE MIXINS ORDER MATTERS
# THEY GO FROM LEFT TO RIGHT



class AnonymousUserMixin:
    def dispatch(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Resolver404


class LoggedInUserMixin:
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Resolver404


# Assume the following mixins have the user authenticated already
class StudentMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Resolver404
        elif request.user.usertype == CustomUser.USERTYPE_DICT["STUDENT"]:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Resolver404


class AgencyMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Resolver404
        elif request.user.usertype == CustomUser.USERTYPE_DICT["AGENCY"]:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Resolver404


class SingleAgentMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Resolver404
        elif request.user.usertype == CustomUser.USERTYPE_DICT["SINGLE_AGENT"]:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Resolver404


class AgentOrAgencyMixin:
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            raise Resolver404
        elif request.user.usertype == CustomUser.USERTYPE_DICT["SINGLE_AGENT"] or request.user.usertype == \
                CustomUser.USERTYPE_DICT["AGENCY"]:
            return super().dispatch(request, *args, **kwargs)
        else:
            raise Resolver404
