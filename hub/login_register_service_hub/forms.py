from django import forms

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser


class EmailRequiredMixin(object):
    def __init__(self, *args, **kwargs):
        super(EmailRequiredMixin, self).__init__(*args, **kwargs)
        # make user email field required
        self.fields['email'].required = True


class LoginRegisterForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=100)
    password = forms.CharField(label="Password", widget=forms.PasswordInput(), max_length=100)


class CreateSingleAgentForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=200)
    password = forms.CharField(label="Password", widget=forms.PasswordInput(), max_length=100)
    first_name = forms.CharField(label="First Name", max_length=200)
    last_name = forms.CharField(label="Last name", max_length=200)


# Need to change the 'create agency form at some point'


class CustomUserCreationForm(EmailRequiredMixin, UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'usertype')


class CustomUserChangeForm(EmailRequiredMixin, UserChangeForm):
    class Meta:
        model = CustomUser
        fields = UserChangeForm.Meta.fields
