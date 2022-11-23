"""
pontos.views - to serve API endpoints
"""

from rest_framework import viewsets
from rest_framework import permissions
from mobilidade_rio.pontos.models import *
from .serializers import *

# from .utils import get_distance, safe_cast
# from .constants import constants


class AgencyViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show agency data
    """

    serializer_class = AgencySerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Agency.objects.all().order_by("agency_id")


class CalendarViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show calendar data
    """

    serializer_class = CalendarSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Calendar.objects.all().order_by("service_id")


class CalendarDatesViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show calendar data
    """

    serializer_class = CalendarDatesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = CalendarDates.objects.all().order_by("service_id")


class RoutesViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show routes data
    """

    serializer_class = RoutesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Routes.objects.all().order_by("route_id")


class TripsViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show trips data
    """
    serializer_class = TripsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Trips.objects.all().order_by("trip_id")
        trip_id = self.request.query_params.get("trip_id")

        if trip_id is not None:
            queryset = queryset.filter(trip_id=trip_id)
        return queryset

        # if code is not None:
        #     qrcode: QrCode = None
        #     try:
        #         qrcode: QrCode = QrCode.objects.get(stop_code=code)
        #     except QrCode.DoesNotExist:
        #         return Trip.objects.none()
        #     sequence: BaseManager = Stop_times.objects.filter(stop_id=qrcode.stop_id)
        #     queryset = queryset.filter(trip_id__in=sequence.values_list('trip_id'))


class ShapesViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show shapes data
    """

    serializer_class = ShapesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Shapes.objects.all().order_by("shape_id")


class StopsViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show stops data
    """

    serializer_class = StopsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Stops.objects.all().order_by("stop_id")
        stop_code = self.request.query_params.get("stop_id")
        if stop_code is not None:
            queryset = queryset.filter(stop_id=stop_code).order_by("stop_id")

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

    """
    API endpoint to show stop_times data
    """
    serializer_class = StopTimesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = StopTimes.objects.all().order_by("trip_id")
        stop_id = None
        # get stop_id from query params
        if 'stop_id' in self.request.query_params:
            stop_id = self.request.query_params.get('stop_id')

        if stop_id is not None and len(stop_id):
            # get multiple stop_ids

            # variables
            table = 'pontos_stoptimes'
            stop_ids = stop_id.split(",")
            stop_ids_formatted = tuple(stop_ids)
            if len(stop_ids) == 1:
                stop_ids_formatted = f"('{stop_id}')"

            # select rows if stop_id in in <stop_ids>
            q_stop_id = f"""
            SELECT * FROM {table} WHERE stop_id IN {stop_ids_formatted}
            """

            # select unique combinations of trip_id and stop_id
            q_trip_ids = f"""
            SELECT DISTINCT trip_id, stop_id FROM ({q_stop_id}) AS t1
            """

            # select if trip_id combines with ALL stop_ids
            q_trip_id_unique = f"""
            SELECT DISTINCT trip_id FROM ({q_trip_ids}) AS t2
            GROUP BY trip_id
            HAVING COUNT(*) = {len(stop_ids)}
            """

            # select rows if trip_id in q_trip_id_unique
            query = f"""
            SELECT * FROM ({q_stop_id}) AS t3
            WHERE trip_id IN ({q_trip_id_unique})
            """

            # execute query
            queryset = queryset.raw(query)
        return queryset


class FrequenciesViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show frequencies data
    """
    serializer_class = FrequenciesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Frequencies.objects.all().order_by("trip_id")
