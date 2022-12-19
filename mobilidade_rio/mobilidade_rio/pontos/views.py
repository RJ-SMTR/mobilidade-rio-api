"""
pontos.views - to serve API endpoints
"""

from rest_framework import viewsets
from rest_framework import permissions
from mobilidade_rio.pontos.models import *
from .serializers import *
from .paginations import LargePagination

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
    pagination_class = LargePagination


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

        stop_code = self.request.query_params.get("stop_code")
        if stop_code is not None:
            # split comma
            stop_code = stop_code.split(",")
            queryset = queryset.filter(stop_code__in=stop_code).order_by("stop_id")

        return queryset


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
            t_stoptimes = 'pontos_stoptimes'
            stop_ids = stop_id.split(",")
            stop_ids_formatted = tuple(stop_ids)
            if len(stop_ids) == 1:
                stop_ids_formatted = f"('{stop_id}')"

            # select unique combinations if stop_id in in <stop_ids>
            q_unique_cols = f"""
            SELECT * FROM (
                SELECT id, trip_id_id, stop_id_id, arrival_time, departure_time,
                ROW_NUMBER() OVER (PARTITION BY trip_id_id, stop_id_id ORDER BY id) AS row_num
                FROM pontos_stoptimes
                WHERE (trip_id_id, stop_id_id, arrival_time, departure_time) IN (
                    SELECT DISTINCT trip_id_id, stop_id_id, arrival_time, departure_time FROM {t_stoptimes}
                    WHERE stop_id_id IN {stop_ids_formatted}
                )
            ) AS q_unique_cols
            WHERE row_num = 1
            """
            query = q_unique_cols

            # execute query
            queryset = queryset.raw(query)

        trip_id = None
        # get trip_id from query params
        if 'trip_id' in self.request.query_params:
            trip_id = self.request.query_params.get('trip_id')
            queryset = queryset.filter(trip_id=trip_id)


        return queryset


class FrequenciesViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show frequencies data
    """
    serializer_class = FrequenciesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Frequencies.objects.all().order_by("trip_id")
