from django import forms

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from login_register_service_hub.models import CustomUser
from .models import Issue


class CreateIssueForm(forms.Form):
    title = forms.CharField(label="title", max_length=200)
    text = forms.CharField(label="text", max_length=200000)


class MessageForm(forms.Form):
    text = forms.CharField(label="text", max_length=20000)

# Create custom admin forms here
