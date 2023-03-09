"""
pontos.views - to serve API endpoints
"""

# stop_code
import operator
from functools import reduce
import django.db.models
from rest_framework.exceptions import ValidationError

# etc
from rest_framework import viewsets
from rest_framework import permissions
from mobilidade_rio.pontos.models import *
import mobilidade_rio.utils.query_utils as qu
from .serializers import *
from .paginations import LargePagination

# import connector to query directly from database
from django.db import connection

cursor = connection.cursor()

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

    def get_queryset(self):
        queryset = Shapes.objects.all().order_by("shape_id")

        # fillter by shape_id
        shape_id = self.request.query_params.get("shape_id")
        if shape_id is not None:
            shape_id = shape_id.split(",")
            queryset = queryset.filter(shape_id__in=shape_id).order_by("shape_id")

        return queryset


class StopsViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show stops data
    """

    serializer_class = StopsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        queryset = Stops.objects.all().order_by("stop_id")

        # filter by stop_id
        stop_id = self.request.query_params.get("stop_id")
        if stop_id is not None:
            queryset = queryset.filter(stop_id=stop_id).order_by("stop_id")

        # filter by stop_code
        stop_code = self.request.query_params.get("stop_code")
        if stop_code is not None:
            # split comma
            stop_code = stop_code.split(",")
            queryset = queryset.filter(stop_code__in=stop_code).order_by("stop_id")

        # filter by stop_name
        stop_name = self.request.query_params.get("stop_name")
        if stop_name is not None:
            stop_name = stop_name.split(",")

            # if any stop_name len is < 4, return custom error message
            for name in stop_name:
                if len(name) < 4:
                    raise ValidationError(
                        {"stop_name": "stop_name must be at least 4 characters long"}
                        )

            # filter if any stop_name is substring, ignore case
            queryset = queryset.filter(
                reduce(
                    operator.or_,
                    (Q(stop_name__icontains=name) for name in stop_name)
                    )
                ).order_by("stop_id")

            # limit final result to 10
            # queryset = queryset[:10]

        return queryset


class StopTimesViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show stop_times data
    """

    serializer_class = StopTimesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        # get real col names and stuff
        TRIP_ID_COL = StopTimes._meta.get_field("trip_id").column
        STOP_ID_COL = StopTimes._meta.get_field("stop_id").column
        PARENT_STATION__STOPS = Stops._meta.get_field("parent_station").column

        queryset = StopTimes.objects.all().order_by("trip_id")
        query = queryset.query

        # increase performance if no need to raw query
        raw_filter_used = False

        # stop_code - parent_station or itself
        stop_code = self.request.query_params.get("stop_code")
        if stop_code is not None:
            stop_code = stop_code.split(",")
            queryset = queryset.filter(
                Q(stop_id__parent_station__stop_code__in=stop_code) |
                Q(stop_id__stop_code__in=stop_code))

        # get stop_id_all
        stop_id__all = self.request.query_params.get("stop_id__all")
        if stop_id__all is not None:
            stop_id__all = stop_id__all.split(",")
            # filter all trips that pass in all stops
            query = qu.q_cols_match_all(
                table=queryset.query, table_is_query=True,
                unique_cols=[TRIP_ID_COL, STOP_ID_COL],
                col_in={STOP_ID_COL: stop_id__all},
                col_match_all=[TRIP_ID_COL],
            )
            raw_filter_used = True

        # stop_id
        stop_id = self.request.query_params.get("stop_id")
        if stop_id is not None:
            stop_id = stop_id.split(",")

            # filter location_type
            location_type = Stops.objects.filter(
                stop_id__in=stop_id).values_list("location_type", flat=True)

            # prevent error on searching inexistent stop_id
            # TODO: filter stop_id or children individually
            if len(location_type):
                # if stop is parent (station), return its children
                if location_type[0] == 1:
                    if raw_filter_used:
                        query = f"""
                        SELECT * FROM ({query}) AS {qu.q_random_hash()}
                        WHERE {STOP_ID_COL} IN (
                            SELECT stop_id FROM pontos_stops
                            WHERE {PARENT_STATION__STOPS} IN ({str(list(stop_id))[1:-1]})
                        )
                        """
                    else:
                        queryset = queryset.filter(
                            stop_id__in=Stops.objects.filter(
                                parent_station__in=stop_id).values_list("stop_id", flat=True)
                        )
                # if stop is child (platform), return searched stops
                if location_type[0] == 0:
                    if raw_filter_used:
                        query = f"""
                        SELECT * FROM ({query}) AS {qu.q_random_hash()}
                        WHERE {STOP_ID_COL} IN ({str(list(stop_id))[1:-1]})
                        """
                    else:
                        queryset = queryset.filter(stop_id__in=stop_id)

        # trip_id
        trip_id = self.request.query_params.get("trip_id")
        if trip_id is not None:
            trip_id = trip_id.split(",")

            if raw_filter_used:
                query = f"""
                SELECT * FROM ({query}) AS {qu.q_random_hash()}
                WHERE {TRIP_ID_COL} IN ({str(list(trip_id))[1:-1]})
                ORDER BY {TRIP_ID_COL}
                """
            else:
                queryset = queryset.filter(
                    trip_id__in=trip_id).order_by("trip_id")

        # execute query
        if raw_filter_used:
            queryset = queryset.raw(query)
        return queryset


class FrequenciesViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show frequencies data
    """

    serializer_class = FrequenciesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Frequencies.objects.all().order_by("trip_id")
