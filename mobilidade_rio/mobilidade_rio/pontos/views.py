from tracemalloc import stop
from django.db.models.manager import BaseManager
from rest_framework import viewsets
from rest_framework import permissions
from .constants import constants
from mobilidade_rio.pontos.models import Agency, Route, Stop, QrCode, Trip, Stop_times
from .serializers import StopSerializer, QrCodeSerializer, AgencySerializer, RouteSerializer, TripSerializer, SequenceSerializer
from .utils import get_distance, safe_cast


class StopViewSet(viewsets.ModelViewSet):
    serializer_class = StopSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Stop.objects.all().order_by("stop_id")
        location = self.request.query_params.get('location', None)
        distance = self.request.query_params.get('distance', None)
        distance = safe_cast(distance, float)
        lat, lon = None, None
        if location is not None:
            lat, lon = self.request.query_params.get('location').split(',')
            lat = safe_cast(lat, float)
            lon = safe_cast(lon, float)
        if (lat is not None) and (lon is not None):
            if distance is None:
                distance = constants.DEFAULT_STOPS_DISTANCE_METERS.value
            queryset = queryset.filter(stop_id__in=[s.stop_id for s in queryset if get_distance(
                (s.stop_lat, s.stop_lon), (lat, lon)) < distance])
        return queryset


class QrCodeViewSet(viewsets.ModelViewSet):
    serializer_class = QrCodeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = QrCode.objects.all().order_by("stop_code")
        code = self.request.query_params.get('code')
        if code is not None:
            queryset = queryset.filter(stop_code=code)
        return queryset


class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.all().order_by("agency_id")
    serializer_class = AgencySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().order_by("route_id")
    serializer_class = RouteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Trip.objects.all().order_by("trip_id")
        code = self.request.query_params.get('code')
        route_id = self.request.query_params.get('route_id')
        if code is not None:
            qrcode: QrCode = None
            try:
                qrcode: QrCode = QrCode.objects.get(stop_code=code)
            except QrCode.DoesNotExist:
                return Trip.objects.none()
            sequence: BaseManager = Stop_times.objects.filter(stop_id=qrcode.stop_id)
            queryset = queryset.filter(trip_id__in=sequence.values_list('trip_id'))
        if route_id is not None:
            queryset = queryset.filter(route_id=route_id)
        return queryset


class SequenceViewSet(viewsets.ModelViewSet):
    serializer_class = SequenceSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Stop_times.objects.all().order_by("stop_id")
        trip_id = self.request.query_params.get('trip')
        stop_id = self.request.query_params.get('stop')
        if trip_id is not None:
            queryset = queryset.filter(trip_id=trip_id).order_by("stop_sequence")
        if stop_id is not None:
            queryset = queryset.filter(stop_id=stop_id).order_by("stop_sequence")
        return queryset
