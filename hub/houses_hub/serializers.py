from rest_framework.serializers import CharField, FloatField, ListField, IntegerField
from houses_hub.models import House, Application, ApplicationInfo
from login_register_service_hub.serializers import *


class HouseSerializer(serializers.ModelSerializer):
    class Meta:
        model = House
        fields = '__all__'


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'


class ApplicationInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationInfo
        fields = '__all__'


class HouseSearchSerializer(serializers.Serializer):
    prince_range = serializers.IntegerField(required=False)
    number_of_beds = serializers.IntegerField(required=False)

    class Meta:
        model = House
        fields = ['max_price', 'min_price']


class PlaceSearchSerializer(HouseSearchSerializer):
    location: CharField = CharField(required=True)
    distance_radius: FloatField = FloatField(required=False)


class DrawingSearchSerializer(HouseSearchSerializer):
    polygon_coordinates = ListField(required=True)


class DistanceToTubeLinesSerializer(HouseSearchSerializer):
    tube_lines = ListField(required=True)
    max_distance = IntegerField(required=True)


class CommuteTimeSearchSerializer(HouseSearchSerializer):
    commute_destiny: CharField = CharField(required=True)
    max_commute_time: IntegerField = IntegerField(required=True)
    transport_mode: CharField = CharField(required=True)
