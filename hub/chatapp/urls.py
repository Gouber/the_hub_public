from django.urls import path
from . import views

app_name = "chatapp"

# Create your views here.
urlpatterns = [
    path('api/create_conversation/', views.CreateConversationAPIView.as_view(), name="api-create-conversation"),
    path('api/create_chat/<int:pk>', views.CreateChatAPIView.as_view(), name="api-create-chat"),
    path('api/chat', views.ListOfChatForConversation.as_view(), name="api-list-chat"),
    path('api/conversation', views.ListConversation.as_view(), name="api-list-conversation"),
    path('api/conversation_with_chat', views.ListConversationWithChat.as_view(), name="api-list-conversation-with-chat"),

]