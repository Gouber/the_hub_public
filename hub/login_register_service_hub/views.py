from typing import Final, Union

from django.contrib.auth.models import AnonymousUser
from django.shortcuts import render
from django.views import View
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_jwt.utils import jwt_decode_handler
from rest_framework_jwt.views import ObtainJSONWebToken

from .forms import LoginRegisterForm, CreateSingleAgentForm
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpRequest, HttpResponse
from django.contrib.auth import login
from django.urls import reverse
from django.contrib.auth import authenticate
from .models import CustomUser
from django.views import generic
from .mixins import AnonymousUserMixin, AgencyMixin, SingleAgentMixin
from django.contrib.auth.views import LogoutView
from django.db.utils import IntegrityError
from django import forms

from .permissions import AnonymousUserPermission
from .serializers import UserSerializerToken


class MyRequest(HttpRequest):
    user: Union[CustomUser, AnonymousUser]


# Inherits from LogoutView so it performs the logout
class HubLogoutView(LogoutView):
    next_page: Final[str] = "login_register_service_hub:login"


# If we change the login/register form modify this
class LoginRegisterView(View):
    form_class: Final[forms.Form] = LoginRegisterForm


class RegisterStudentView(AnonymousUserMixin, LoginRegisterView):
    template: Final[str] = "login_register_service_hub/register.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template, {"form": self.form_class()})

    def post(self, request: HttpRequest) -> HttpResponse:
        form: Final[forms.Form] = self.form_class(request.POST)

        if form.is_valid():
            email: Final[str] = form.cleaned_data['email']
            password: Final[str] = form.cleaned_data['password']
            try:
                user: Final[CustomUser] = CustomUser.objects.create_user(email=email, password=password,
                                                                         username=email.split("@")[0])
            except IntegrityError:
                return HttpResponseBadRequest("Student Already Exists")
            else:
                # Note how we preserve the created user so we can log him in
                # This is not true when creating agents as the agency creates the agents.
                login(request, user)
                return HttpResponseRedirect(reverse('houses_hub:home'))
        else:
            return HttpResponseBadRequest("Invalid Form")


class CreateAgentView(AgencyMixin, View):
    template: Final[str] = "login_register_service_hub/create_single_agent.html"
    form_class: Final[forms.Form] = CreateSingleAgentForm

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template, {"form": self.form_class()})

    def post(self, request: HttpRequest) -> HttpResponse:
        form: Final[forms.Form] = self.form_class(request.POST)

        if form.is_valid():
            email: Final[str] = form.cleaned_data['email']
            password: Final[str] = form.cleaned_data['password']
            first_name: Final[str] = form.cleaned_data['first_name']
            last_name: Final[str] = form.cleaned_data['last_name']
            try:
                CustomUser.objects.create_user(email=email, password=password, first_name=first_name,
                                               last_name=last_name, username=email.split("@")[0], usertype=3,
                                               agency=request.user)
            except IntegrityError:
                return HttpResponseBadRequest("Agent Already Exists")
            else:
                return HttpResponseRedirect(reverse('login_register_service_hub:created_single_agent'))
        else:
            return HttpResponseBadRequest("Invalid Form")


class CreateAgency(AnonymousUserMixin, View):
    template: Final[str] = "login_register_service_hub/create_agency.html"
    form_class: Final[forms.Form] = LoginRegisterForm

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template, {"form": self.form_class()})

    def post(self, request: HttpRequest) -> HttpResponse:

        form: Final[forms.Form] = self.form_class(request.POST)

        if form.is_valid():
            email: Final[str] = form.cleaned_data['email']
            password: Final[str] = form.cleaned_data['password']
            try:
                user: Final[CustomUser] = CustomUser.objects.create_user(email=email, password=password,
                                                                         username=email.split("@")[0],
                                                                         usertype=2)
            except IntegrityError:
                return HttpResponseBadRequest("Agency Already Exists")
            else:
                login(request, user)
                return HttpResponseRedirect(reverse('login_register_service_hub:created_agency'))
        else:
            return HttpResponseBadRequest("Invalid Form")


class LoginView(AnonymousUserMixin, LoginRegisterView):
    template: Final[str] = "login_register_service_hub/login.html"

    def get(self, request: HttpRequest) -> HttpResponse:
        return render(request, self.template, {"form": self.form_class()})

    def post(self, request: HttpRequest) -> HttpResponse:

        form: Final[forms.Form] = self.form_class(request.POST)

        if form.is_valid():
            email: Final[str] = form.cleaned_data["email"]
            password: Final[str] = form.cleaned_data["password"]

            user: Final[Union[CustomUser, None]] = authenticate(username=email, password=password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse("houses_hub:home"))
            else:
                return render(request, self.template,
                              {"error_message": "Email/password did not match", "form": self.form_class()})
        else:
            return HttpResponseBadRequest("Invalid Form")


class CreatedAgentView(SingleAgentMixin, generic.TemplateView):
    template_name: Final[str] = 'polls/created.html'


class CreatedAgencyView(AgencyMixin, generic.TemplateView):
    template_name: Final[str] = 'polls/created_agency.html'


class APIRegisterStudent(APIView):
    permission_classes = [AnonymousUserPermission, ]

    def post(self, request, format=None):
        data = UserSerializerToken(data=request.data)
        if data.is_valid():
            data.save()
            return Response(data.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)


class APIRegisterAgency(APIView):
    permission_classes = [AnonymousUserPermission, ]

    def post(self, request, format=None):
        data = UserSerializerToken(data=request.data)
        if data.is_valid():
            data.save(usertype=2)
            return Response(data.data, status=status.HTTP_201_CREATED)
        else:
            return Response(data.errors, status=status.HTTP_400_BAD_REQUEST)

