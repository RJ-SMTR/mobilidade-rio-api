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

    def get_queryset(self):
        queryset = StopTimes.objects.all().order_by("trip_id")
        stop_id = None
        # get stop_id from query params
        if 'stop_id' in self.request.query_params:
            stop_id = self.request.query_params.get('stop_id')

        if stop_id is not None:
            # get multiple stop_ids
            stop_ids = stop_id.split(",")
            stops = queryset.filter(stop_id__in=stop_ids)

            # If some stop_id from input is not in results, return empty
            stop_id_list = stops.order_by("stop_id").values_list('stop_id', flat=True).distinct()
            if len(stop_id_list) != len(stop_ids):
                return queryset.none()
            
            # filter if trips passing by all stop_ids
            trip_id_list = stops.order_by('trip_id').values_list('trip_id', flat=True).distinct()
            trip_id_list = [str(trip_id) for trip_id in trip_id_list]
            stops = stops.filter(trip_id__in=trip_id_list)

            # filter if trips passing by all stop_ids
            stop_id_queries = [stops.filter(stop_id=_stop_id) for _stop_id in stop_ids]
            for trip_id in list(trip_id_list):
                for stop_query in stop_id_queries:
                    query = stop_query.filter(trip_id=trip_id)
                    if not query:
                        trip_id_list.remove(trip_id)
                        break

            queryset = stops.filter(trip_id__in=trip_id_list)

            # order by
            queryset = queryset.order_by("trip_id", "stop_sequence")

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
