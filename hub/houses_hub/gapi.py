import math
import requests
import googlemaps
from typing import *

gmaps = googlemaps.Client(key='')


class Coordinates():
    def __init__(self, lat: float, long: float):
        self.latitude: float = lat
        self.longitude: float = long


class GAPI:

    @staticmethod
    def distance_between(lat1, lon1, lat2, lon2):
        r: int = 6371
        dLat: float = (lat2 - lat1) * math.pi / 180
        dLon: float = (lon2 - lon1) * math.pi / 180
        a: float = math.sin(dLat / 2) * math.sin(dLat / 2) + math.cos(lat1 * math.pi / 180) * math.cos(
            lat2 * math.pi / 180) * math.sin(dLon / 2) * math.sin(dLon / 2)
        c: float = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        d: float = r * c
        return d

    @staticmethod
    def time_distance_between(origin, destination, transport_mode):
        gmaps.distance_matrix(origins=origin, destinations=destination, transport_mode=transport_mode)

    @staticmethod
    def extract_coordinates(address: str) -> Union[Coordinates, None]:
        geocode_result = gmaps.geocode(address=address + "+UK")
        if len(geocode_result) == 0:
            return None
        else:
            lat = geocode_result[0]["geometry"]["location"]["lat"]
            lon = geocode_result[0]["geometry"]["location"]["lng"]
            return Coordinates(lat, lon)


class TFL:
    appId = ""
    appKey = ""
    params = {"app_id": appId, "app_key": appKey}
    URL = "https://api.tfl.gov.uk/"

    @property
    def tube_lines_ids(self):
        response = requests.get(url=self.URL + "Line/Mode/tube", params=self.params)
        return [line["id"] for line in response.json()]

    def line_station_coordinates(self, line_id):
        subparams = {"tflOperatedNationalRailStationsOnly": "false"}
        response = requests.get(url=self.URL + "Line/" + line_id + "/StopPoints",
                                params={**self.params, **subparams})
        return [Coordinates(station["lat"], station["lon"]) for station in response.json()]
