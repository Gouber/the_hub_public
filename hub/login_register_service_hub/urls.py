from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
from . import views
from django.views.generic import TemplateView
from .views import APIRegisterStudent,  APIRegisterAgency

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


app_name = "login_register_service_hub"

# Need to remember to protect most of these
urlpatterns = [
    path('', views.LoginView.as_view(), name="login"),
    # This is to register a student
    path('logout/', views.HubLogoutView.as_view(), name="logout"),
    # This is to logout any user
    path('register/', views.RegisterStudentView.as_view(), name="register"),
    # This is to create a single agent
    path('create_agent/', views.CreateAgentView.as_view(), name="create_agent"),
    # This is what happens after the agent has been created
    path('created_agent/', TemplateView.as_view(template_name="login_register_service_hub/created.html"),
         name="created_single_agent"),
    # This is where we create agencies
    path('create_agency/', views.CreateAgency.as_view(), name="create_agency"),
    # This is what happens after a single agency has been created
    path('created_agency/', TemplateView.as_view(template_name="login_register_service_hub/created_agency.html"),
         name="created_agency"),


    path('api/register-student/', APIRegisterStudent.as_view(), name="api-register-student"),
    path('api/login/', TokenObtainPairView.as_view(), name="api-login"),
    path('api/refresh-token/', TokenRefreshView.as_view(), name="api-refresh-token"),
    path('api/token/verify/', TokenVerifyView.as_view(), name='api-token_verify'),
    path('api/register-agency/', APIRegisterAgency.as_view(), name="api-register-agency")
]
