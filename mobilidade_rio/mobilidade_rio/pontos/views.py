from tracemalloc import stop
from django.db.models.manager import BaseManager
from rest_framework import viewsets
from rest_framework import permissions
from .constants import constants
from .models import Mode, Stop, QrCode, Linha, Agency, Route, Trip, Sequence
from .serializers import ModeSerializer, StopSerializer, QrCodeSerializer, LinhaSerializer, AgencySerializer, RouteSerializer, TripSerializer, SequenceSerializer
from .utils import get_distance, safe_cast


class ModeViewSet(viewsets.ModelViewSet):
    queryset = Mode.objects.all().order_by("id")
    serializer_class = ModeSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class StopViewSet(viewsets.ModelViewSet):
    serializer_class = StopSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Stop.objects.all().order_by("id")
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
            queryset = queryset.filter(id__in=[s.id for s in queryset if get_distance(
                (s.latitude, s.longitude), (lat, lon)) < distance])
        return queryset


class QrCodeViewSet(viewsets.ModelViewSet):
    serializer_class = QrCodeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = QrCode.objects.all().order_by("code")
        code = self.request.query_params.get('code')
        if code is not None:
            queryset = queryset.filter(code=code)
        return queryset


class LinhaViewSet(viewsets.ModelViewSet):
    queryset = Linha.objects.all().order_by("id")
    serializer_class = LinhaSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class AgencyViewSet(viewsets.ModelViewSet):
    queryset = Agency.objects.all().order_by("id")
    serializer_class = AgencySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class RouteViewSet(viewsets.ModelViewSet):
    queryset = Route.objects.all().order_by("id")
    serializer_class = RouteSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class TripViewSet(viewsets.ModelViewSet):
    serializer_class = TripSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Trip.objects.all().order_by("id")
        code = self.request.query_params.get('code')
        route_id = self.request.query_params.get('route_id')
        if code is not None:
            qrcode: QrCode = None
            try:
                qrcode: QrCode = QrCode.objects.get(code=code)
            except QrCode.DoesNotExist:
                return Trip.objects.none()
            sequence: BaseManager = Sequence.objects.filter(stop=qrcode.stop)
            queryset = queryset.filter(id__in=sequence.values_list('trip'))
        if route_id is not None:
            queryset = queryset.filter(route=route_id)
        return queryset


class SequenceViewSet(viewsets.ModelViewSet):
    serializer_class = SequenceSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Sequence.objects.all().order_by("id")
        trip_id = self.request.query_params.get('trip_id')
        stop_id = self.request.query_params.get('stop_id')
        if trip_id is not None:
            queryset = queryset.filter(trip=trip_id).order_by("order")
        if stop_id is not None:
            queryset = queryset.filter(stop=stop_id).order_by("order")
        return queryset
