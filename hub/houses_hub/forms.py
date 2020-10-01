from django import forms
from django.forms import CharField, FloatField
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from login_register_service_hub.models import CustomUser
from .models import Application, House


class CreateApplicationForm(forms.Form):
    students: CharField = CharField(label="students", max_length=200)


class UserInfoForm(forms.Form):
    personal_details: CharField = CharField(label="personal_details", max_length=500)
    money = CharField(label="money", max_length=200)
    letter_of_recommendation: CharField = forms.CharField(label="money", max_length=2000)


