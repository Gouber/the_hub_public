from typing import Final
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from login_register_service_hub.permissions import StudentWithLeasePermission
from .models import Issue, Message
from login_register_service_hub.models import CustomUser
from django.utils import timezone
from houses_hub.models import House, Lease
from django.http import Http404
from .serializers import IssueSerializer, IssueWithMessageSerializer, MessageCreateSerializer, MessageListSerializer


class MetaData:
    USERTYPE_DICT = {
        1: "STUDENT",
        2: "AGENCY",
        3: "SINGLE_AGENT"
    }


class APIIssueIndexView(generics.ListAPIView):
    serializer_class = IssueSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        house: Final[House] = get_object_or_404(House, pk=self.kwargs['house_id'])
        user = self.request.user
        if user.is_authenticated:
            if CustomUser.USERTYPE_DICT["AGENCY"] == user.usertype:
                if house.agency == user:
                    return Issue.objects.filter(house=house)
                else:
                    return Issue.objects.filter(house=house, hidden=False)
            if CustomUser.USERTYPE_DICT["STUDENT"] == user.usertype:
                if Lease.objects.filter(students=user, house=house).exists():
                    return Issue.objects.filter(house=house)
                else:
                    return Issue.objects.filter(house=house, hidden=False)
        else:
            return Issue.objects.filter(house=house, hidden=False)


class APICreateIssueView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, StudentWithLeasePermission, ]
    serializer_class = IssueWithMessageSerializer

    def create(self, request, *args, **kwargs):
        serializer = IssueWithMessageSerializer(data=request.data)

        if serializer.is_valid():
            house = get_object_or_404(House, pk=self.kwargs['house_id'])
            if Lease.objects.filter(students=self.request.user).exists():
                serializer.save(user=self.request.user, pub_date=timezone.now(), house=house)
                return Response(status=status.HTTP_201_CREATED)
            else:
                raise Http404
        else:
            errors = serializer.error_messages
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


class APIIssueMessageIndexView(generics.ListAPIView):
    serializer_class = MessageListSerializer
    permission_classes = [AllowAny, ]

    def get_queryset(self):
        issue = get_object_or_404(Issue, pk=self.kwargs['issue_id'])
        if issue.hidden:
            if self.request.user.is_authenticated:
                user = self.request.user
                if user.usertype == CustomUser.USERTYPE_DICT["AGENCY"]:
                    if issue.house.agency == user:
                        return Message.objects.filter(issue=issue).order_by("date_sent")
                    else:
                        raise Http404
                elif user.usertype == CustomUser.USERTYPE_DICT["STUDENT"]:
                    if Lease.objects.filter(students=user, house=issue.house).exists():
                        return Message.objects.filter(issue=issue).order_by("date_sent")
                    else:
                        raise Http404
                else:
                    raise Http404
            else:
                raise Http404
        else:
            return Message.objects.filter(issue=issue).order_by("date_sent")


class APIIssueMessageCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated, StudentWithLeasePermission, ]
    serializer_class = MessageCreateSerializer

    def create(self, request, *args, **kwargs):
        issue = get_object_or_404(Issue, pk=self.kwargs['issue_id'])
        if Lease.objects.filter(students=self.request.user, house=issue.house).exists():
            msg_ser = MessageCreateSerializer(data=request.data)
            if msg_ser.is_valid():
                msg_ser.save(user=self.request.user, issue=issue)
                return Response(status=status.HTTP_201_CREATED)
            else:
                return Response(data=msg_ser.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            raise Http404


class APIIssueMessageCloseView(APIView):
    permission_classes = [IsAuthenticated, StudentWithLeasePermission, ]

    def get(self, request, *args, **kwargs):
        user = self.request.user
        issue = get_object_or_404(Issue, pk=kwargs.get('issue_id'))

        if Lease.objects.filter(students=user, house=issue.house).exists():
            issue.closed = True
            issue.save()
            return Response(status=status.HTTP_202_ACCEPTED)
        else:
            raise Http404
