# from tracemalloc import stop
from django.db.models.manager import BaseManager
from rest_framework import viewsets
from rest_framework import permissions
from mobilidade_rio.pontos.models import *
from .serializers import *

# from .utils import get_distance, safe_cast
# from .constants import constants


class AgencyViewSet(viewsets.ModelViewSet):
    serializer_class = AgencySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Agency.objects.all().order_by("agency_id")


class CalendarViewSet(viewsets.ModelViewSet):
    serializer_class = CalendarSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Calendar.objects.all().order_by("service_id")


class CalendarDatesViewSet(viewsets.ModelViewSet):
    serializer_class = CalendarDatesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = CalendarDates.objects.all().order_by("service_id")


class RoutesViewSet(viewsets.ModelViewSet):
    serializer_class = RoutesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Routes.objects.all().order_by("route_id")


class TripsViewSet(viewsets.ModelViewSet):
    serializer_class = TripsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Trips.objects.all().order_by("trip_id")
        trip_id = self.request.query_params.get("trip_id")

        if trip_id is not None:
            queryset = queryset.filter(trip_id=trip_id)
        return queryset


#     #     if code is not None:
#     #         qrcode: QrCode = None
#     #         try:
#     #             qrcode: QrCode = QrCode.objects.get(stop_code=code)
#     #         except QrCode.DoesNotExist:
#     #             return Trip.objects.none()
#     #         sequence: BaseManager = Stop_times.objects.filter(stop_id=qrcode.stop_id)
#     #         queryset = queryset.filter(trip_id__in=sequence.values_list('trip_id'))


class ShapesViewSet(viewsets.ModelViewSet):
    serializer_class = ShapesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Shapes.objects.all().order_by("shape_id")


class StopsViewSet(viewsets.ModelViewSet):
    serializer_class = StopsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Stops.objects.all().order_by("stop_id")
        stop_code = self.request.query_params.get(
            "stop_id"
        )  # todo: trocar para stop_code quando preenchido

        if stop_code is not None:
            queryset = queryset.filter(stop_id=stop_code).order_by(
                "stop_id"
            )  # todo: trocar para stop_code quando preenchido

        return queryset

    #     location = self.request.query_params.get('location', None)
    #     distance = self.request.query_params.get('distance', None)
    #     distance = safe_cast(distance, float)
    #     lat, lon = None, None
    #     if location is not None:
    #         lat, lon = self.request.query_params.get('location').split(',')
    #         lat = safe_cast(lat, float)
    #         lon = safe_cast(lon, float)
    #     if (lat is not None) and (lon is not None):
    #         if distance is None:
    #             distance = constants.DEFAULT_STOPS_DISTANCE_METERS.value
    #         queryset = queryset.filter(stop_id__in=[s.stop_id for s in queryset if get_distance(
    #             (s.stop_lat, s.stop_lon), (lat, lon)) < distance])
    #     return queryset


class StopTimesViewSet(viewsets.ModelViewSet):
    serializer_class = StopTimesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(
        self,
    ):  # todo: poder filtrar por mais de 1 stop_id (inclusivo) - pergunta: quais sao todas as trips que passam nos X pontos?
        queryset = StopTimes.objects.all().order_by("trip_id")
        stop_id = self.request.query_params.get("stop_id")

        if stop_id is not None:
            queryset = queryset.filter(stop_id=stop_id).order_by("trip_id")

        return queryset


#     # def get_queryset(self):
#     #     queryset = Stop_times.objects.all().order_by("stop_id")
#     #     trip_id = self.request.query_params.get('trip')
#     #     stop_id = self.request.query_params.get('stop')
#     #     if trip_id is not None:
#     #         queryset = queryset.filter(trip_id=trip_id).order_by("order")
#     #     if stop_id is not None:
#     #         queryset = queryset.filter(stop_id=stop_id).order_by("order")
#     #     return queryset


class FrequenciesViewSet(viewsets.ModelViewSet):
    serializer_class = FrequenciesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Frequencies.objects.all().order_by("trip_id")
