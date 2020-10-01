from django.urls import path
from . import views
from typing import Final
from .views import CreateHouseView

app_name: Final[str] = "houses_hub"

urlpatterns = [

    path('api/create-house', CreateHouseView.as_view(), name = "api-create-house"),
    path('', views.HomeView.as_view(), name="home"),
    path('index/', views.HousesIndexView.as_view(), name="index"),
    path('search/place/', views.PlaceSearchView.as_view(), name="place_house_search"),
    path('search/drawing/', views.DrawingSearchView.as_view(), name="drawing_house_search"),
    path('search/tube_line/', views.DistanceToTubeSearchView.as_view(), name="distance_to_line_house_search"),
    path('search/commute_time/', views.CommuteTimeSearchView.as_view(), name="commute_time_house_search"),
    path('<int:pk>/', views.HouseDetailView.as_view(), name="detail"),
    path('apply/<int:pk>/', views.CreateApplicationView.as_view(), name="create_application"), # add all the users to the application
    path('application/<int:pk>/', views.FillUserApplicationInfoView.as_view(), name="fill_application_info"), # add the application information, if information has been given, overwrite it
    path('application/accept/<int:pk>/', views.AcceptApplicationView.as_view(), name="accept_application"), # accept an application you've been added to as a student

    path('application/pending/index/', views.PendingApplicationIndexView.as_view(), name="pending_application_index"), # student indexview of applications that haven't been accepted or rejected by the student
    path('application/edit/index/', views.EditApplicationIndexView.as_view(), name="edit_application_index"), # index view of all the open applications of the student 
    path('received-applications/<int:pk>', views.ReceivedApplicationsIndexView.as_view(), name="received_applications"), # agency and agent index of recevied applications for a spceific house 
    path('received-applications/accept/<int:pk>/', views.AcceptReceivedApplicationView.as_view(), # accept or deny an application for a specific house  
         name="accept_received_application"),
    path('managed-houses/', views.ManagedHousesIndexView.as_view(), name="managed_houses"), # agency or agent index page of managed houses
    path('create/', views.CreateHouseView.as_view(), name="create") # agency or agent to create houses
]
