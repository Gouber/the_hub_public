from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from rest_framework.authtoken.models import Token

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    fieldsets = (
        (('User'),
         {'fields': ('username', 'email', 'is_staff', 'usertype', 'first_name', 'last_name', 'password', 'agency')}),
    )


admin.site.register(CustomUser, CustomUserAdmin)

# Register your models here.
