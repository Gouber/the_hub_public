from django.urls import path
from . import views

app_name = "issues"

# Create your views here.
urlpatterns = [
    path('api/issue-index/<int:house_id>/', views.APIIssueIndexView.as_view(), name="api-issue-index"),
    path('api/issue-create/<int:house_id>', views.APICreateIssueView.as_view(), name="api-issue-create"),
    path('api/issue-chat/<int:issue_id>/', views.APIIssueMessageIndexView.as_view() ,name = "api-issue-chat"),
    path('api/issue-chat/create/<int:issue_id>', views.APIIssueMessageCreateView.as_view(), name="api-issue-create-chat"),
    path('api/issue-chat/close/<int:issue_id>', views.APIIssueMessageCloseView.as_view(), name="api-issue-close-chat")
]
