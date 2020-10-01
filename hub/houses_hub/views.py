from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import QuerySet
from django.utils import timezone
from rest_framework import status
from rest_framework.utils import json
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.request import Request
from login_register_service_hub.mixins import AgentOrAgencyMixin, StudentMixin
from shapely.geometry import Point, Polygon
from .gapi import GAPI, Coordinates, TFL
from .models import House, Lease
from .permissions import StudentPermission
from .serializers import HouseSearchSerializer, PlaceSearchSerializer, DrawingSearchSerializer, \
    DistanceToTubeLinesSerializer, CommuteTimeSearchSerializer
from .view_utils import *
from typing import *

# Create your views here.
from .serializers import HouseSerializer, ApplicationSerializer, ApplicationInfoSerializer


class ListHousesView(ListAPIView):
    queryset = House.objects.all()
    serializer_class = HouseSerializer


class CreateHouseView(AgentOrAgencyMixin, generics.CreateAPIView):
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = HouseSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            if House.objects.filter(address=serializer.validated_data["address"]).exists():
                return Response(data="house with the address provided already exists",
                                status=status.HTTP_400_BAD_REQUEST)
            coords: Coordinates = GAPI.extract_coordinates(serializer.validated_data["address"])
            if coords is None:
                return Response(data="Address doesn't exist", status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer.save(agency=request.user, lat=coords.latitude, lgn=coords.longitude)
                return Response(status=status.HTTP_201_CREATED)
        else:
            errors = serializer.error_messages
            return Response(data=errors, status=status.HTTP_400_BAD_REQUEST)


class HomeView(APIView):
    permission_classes = [AllowAny, ]

    # TODO This needs a serializer
    def post(self, request, *args, **kwargs):
        close_houses: List[House] = []
        address: Final[str] = request.data['address']
        coords: Coordinates = GAPI.extract_coordinates(address)
        max_dist: Final[int] = 5
        for house in House.objects.all():
            # make sure it's not the same house after adding more parameters
            if GAPI.distance_between(coords.latitude, coords.longitude, float(house.lat), float(house.lgn)) < max_dist:
                close_houses.append(house)
        else:
            pass
        serializer = HouseSerializer(close_houses, many=True)
        return Response(data=serializer.data, status=status.HTTP_302_FOUND)


class HousesIndexView(generics.ListAPIView):
    permission_classes = [AllowAny, ]
    serializer_class = HouseSerializer
    queryset = House.objects.all()


class HouseDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny, ]

    def retrieve(self, request, *args, **kwargs):
        house = get_object_or_404(House, pk=kwargs['pk'])
        serializer = HouseSerializer(house)
        return Response(data=serializer.data, status=status.HTTP_200_OK)


class CreateApplicationView(APIView):
    permission_classes = [IsAuthenticated, StudentPermission, ]

    def get(self, request, *args, **kwargs):
        try:
            house = House.objects.get(pk=kwargs['pk'])
        except House.DoesNotExist:
            return Response(data={'response': ERROR_HOUSE_DOES_NOT_EXIST})
        serializer = HouseSerializer(house)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        try:
            house = House.objects.get(pk=kwargs['pk'])
        except House.DoesNotExist:
            return Response(data={'response': ERROR_HOUSE_DOES_NOT_EXIST})
        sender = request.user
        students_list: Final[List[str]] = json.loads(request.data['students'])
        if not students_list:
            student_object_list: Union[None, List[CustomUser]] = None
        else:
            # Should only work if all emails belong to students and the students are different from the sender
            # Emails can't be repeated
            student_object_list: Union[None, List[CustomUser]] = []
            for st in students_list:
                try:
                    student = CustomUser.objects.get(email=st)
                except ObjectDoesNotExist:
                    return Response(data={'response': ERROR_STUDENT_DOES_NOT_EXIST}, status=status.HTTP_400_BAD_REQUEST)
                else:
                    if is_email_of_unique_student_in_application(sender=sender, student=student,
                                                                 accumulated_students=student_object_list):
                        student_object_list.append(student)
                    else:
                        return Response(data={"response": ERROR_REPEATED_STUDENT}, status=status.HTTP_400_BAD_REQUEST)
        application = Application.objects.create(house=house, submitted=False)
        if student_object_list:
            application.students.add(*student_object_list)
            application.save()
        sender_info = ApplicationInfo.objects.create(student=sender, application=application)
        serializer = ApplicationInfoSerializer(sender_info)
        return Response(data=serializer.data, status=status.HTTP_302_FOUND)


class FillUserApplicationInfoView(APIView):
    permission_classes = [IsAuthenticated, StudentPermission, ]

    def get(self, request, *args, **kwargs):
        if not student_owns_application_info(request.user, kwargs['pk']):
            return Response(data={'response': ERROR_NOT_APPLICATION_INFO_OWNER},
                            status=status.HTTP_401_UNAUTHORIZED, )
        application_info = ApplicationInfo.objects.get(pk=kwargs['pk'])
        serializer = ApplicationInfoSerializer(application_info)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        if not student_owns_application_info(request.user, kwargs['pk']):
            return Response(data={'response': ERROR_NOT_APPLICATION_INFO_OWNER},
                            status=status.HTTP_401_UNAUTHORIZED, )
        application_info = ApplicationInfo.objects.get(pk=kwargs['pk'])
        application_info.personal_details = request.data['personal_details']
        application_info.money = request.data['money']
        application_info.letter_of_recommendation = request.data['letter_of_recommendation']
        application_info.save()
        if is_last_student_to_accept_application(application_info):
            should_submit_application: Final[str] = request.data['submit_application']
            if should_submit_application == "yes":
                application: Application = application_info.application
                application.submitted = True
                application.save()
                return Response(data={'response': APPLICATION_SUBMITTED}, status=status.HTTP_302_FOUND)
        return Response(data={'response': APPLICATION_INFO_SAVED}, status=status.HTTP_302_FOUND)


class AcceptApplicationView(APIView):
    permission_classes = [IsAuthenticated, StudentPermission, ]

    def get(self, request, *args, **kwargs):
        if not api_is_student_pending_in_application(request.user, kwargs['pk']):
            return Response(data={'response': ERROR_STUDENT_NOT_IN_APPLICATION},
                            status=status.HTTP_404_NOT_FOUND, )
        application = Application.objects.get(pk=kwargs['pk'])
        serializer = ApplicationSerializer(application)
        return Response(data=serializer.data, status=status.HTTP_200_OK, )

    def post(self, request, *args, **kwargs):
        if not api_is_student_pending_in_application(request.user, kwargs['pk']):
            return Response(data={'response': ERROR_STUDENT_NOT_IN_APPLICATION},
                            status=status.HTTP_404_NOT_FOUND, )
        application = Application.objects.get(pk=self.kwargs['pk'])
        selected_choice: Final[str] = request.data['choice']
        if selected_choice == "Accept":
            application.students.remove(request.user)
            application.save()
            student_info = ApplicationInfo.objects.create(application=application, student=request.user)
            serializer = ApplicationInfoSerializer(student_info)
            return Response(serializer.data, status=status.HTTP_302_FOUND)
        elif selected_choice == "Reject":
            # Deleting the application for now
            application.delete()
            return Response({'response': APPLICATION_DELETED}, status=status.HTTP_302_FOUND)
        else:
            return Response(data={'response': ERROR_INVALID_INPUT},
                            status=status.HTTP_400_BAD_REQUEST, )


class PendingApplicationIndexView(StudentMixin, ListAPIView):
    serializer_class = ApplicationSerializer

    def get_queryset(self) -> QuerySet:
        return self.request.user.application_set.all()


class EditApplicationIndexView(StudentMixin, ListAPIView):
    serializer_class = ApplicationInfoSerializer

    def get_queryset(self) -> QuerySet:
        return ApplicationInfo.objects.filter(student=self.request.user, application__submitted=False)


# should it be students & submitted? ApplicationInfo doesnt have the fields in line above
class ReceivedApplicationsIndexView(AgentOrAgencyMixin, ListAPIView):
    serializer_class = ApplicationSerializer

    def get_queryset(self) -> QuerySet:
        house: Final[House] = get_object_or_404(House, agency=extract_agency(self.request.user))
        return Application.objects.filter(house=house, submitted=True)


class AcceptReceivedApplicationView(AgentOrAgencyMixin, APIView):
    def post(self, request: Request, **kwargs) -> Response:
        application: Final[Union[Http404, Application]] = agency_owns_application_or_404(request.user, kwargs["pk"])
        if 'choice' in request.data:
            selected_choice: Final[str] = request.data['choice']
            if selected_choice == "Accept":
                lease: Lease = Lease(house=application.house, expiration_date=timezone.now() + timedelta(days=30))
                lease.save()
                students_info = ApplicationInfo.objects.filter(application=application)
                students = [student_info.student for student_info in students_info]
                students_info.delete()
                application.delete()
                for student in students:
                    student.lease = lease
                    student.save()
                res = Response(status=status.HTTP_200_OK)
                return res
            elif selected_choice == "Reject":
                ApplicationInfo.objects.filter(application=application).delete()
                application.delete()
                return Response(status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class ManagedHousesIndexView(AgentOrAgencyMixin, ListAPIView):
    serializer_class = HouseSerializer

    def get_queryset(self) -> QuerySet:
        return House.objects.filter(agency=extract_agency(self.request.user))


class HouseSearchView(ListAPIView):
    serializer_class = HouseSerializer
    input_serializer_class = HouseSearchSerializer

    def get_queryset(self) -> QuerySet:
        max_price = int(self.request.GET.get("max_price"))
        min_price = int(self.request.GET.get("min_price"))
        return House.objects.filter(price__level__lte=max_price, price__level_gte=min_price)


class PlaceSearchView(HouseSearchView):
    input_serializer_class = PlaceSearchSerializer

    def get_queryset(self) -> QuerySet:
        filtered_houses: QuerySet = super().get_queryset()

        coords: Coordinates = GAPI.extract_coordinates(self.request.GET.get("location"))
        distance_radius = int(self.request.GET.get("distance_radius"))
        pk_set = []
        for house in filtered_houses:
            if GAPI.distance_between(coords.latitude, coords.longitude, float(house.lat),
                                     float(house.lgn)) < distance_radius:
                pk_set.append(house.pk)
        return filtered_houses.filter(pk__in=pk_set)


class DrawingSearchView(HouseSearchView):
    input_serializer_class = DrawingSearchSerializer

    def get_queryset(self) -> QuerySet:
        filtered_houses = super().get_queryset()
        polygon_coordinates = self.request.GET.get("polygon_coordinates")
        polygon = Polygon(polygon_coordinates)
        pk_set = []
        for house in filtered_houses:
            if polygon.contains(Point(house.lat, house.lgn)):
                pk_set.append(house.pk)
        return filtered_houses.filter(pk__in=pk_set)


class DistanceToTubeSearchView(HouseSearchView):
    input_serializer_class = DistanceToTubeLinesSerializer

    def get_queryset(self) -> QuerySet:
        filtered_houses = super().get_queryset()
        tube_lines_ids = self.request.GET.get("tube_lines_ids")
        max_distance = self.request.GET.get("max_distance")
        tfl = TFL()
        pk_set = set()
        for house in filtered_houses:
            for id in tube_lines_ids:
                for coords in tfl.line_station_coordinates(id):
                    if GAPI.distance_between(coords.latitude, coords.longitude, float(house.lat),
                                             float(house.lgn)) < max_distance:
                        pk_set.add(house.pk)
        return filtered_houses.filter(pk__in=pk_set)


class CommuteTimeSearchView(HouseSearchView):
    input_serializer_class = CommuteTimeSearchSerializer

    def get_queryset(self) -> QuerySet:
        filtered_houses = super().get_queryset()
        commute_destiny = self.request.GET.get("commute_destiny")
        max_commute_time = self.request.GET.get("max_commute_time")
        transport_mode = self.request.GET.get("transport_mode")
        pk_set = {}
        for house in filtered_houses:
            if GAPI.time_distance_between({"lat": house.lat, "lng": house.lon}, commute_destiny,
                                          transport_mode) < max_commute_time:
                pk_set.append(house.pk)
        return filtered_houses.filter(pk__in=pk_set)
