"""
pontos.views - to serve API endpoints
"""

from rest_framework import viewsets
from rest_framework import permissions
from mobilidade_rio.pontos.models import *
import mobilidade_rio.utils.query_utils as qu
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

    def get_queryset(self):
        queryset = Agency.objects.all().order_by("agency_id")

        # filter by route_type
        route_type = self.request.query_params.get("route_type")
        if route_type is not None:
            route_type = route_type.split(",")
            routes = Routes.objects.filter(route_type__in=route_type)
            queryset = queryset.filter(agency_id__in=routes.values_list("agency_id", flat=True)).order_by("agency_id")

        return queryset


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

    def get_queryset(self):
        queryset = Routes.objects.all().order_by("route_id")

        # fillter by route_id
        route_id = self.request.query_params.get("route_id")
        if route_id is not None:
            queryset = queryset.filter(route_id=route_id).order_by("route_id")

        # filter by route_type
        route_type = self.request.query_params.get("route_type")
        if route_type is not None:
            queryset = queryset.filter(route_type=route_type).order_by("route_id")

        return queryset


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

        # filter by route_type
        route_type = self.request.query_params.get("route_type")
        if route_type is not None:
            route_type = route_type.split(",")
            routes = Routes.objects.filter(route_type__in=route_type)
            queryset = queryset.filter(route_id__in=routes.values_list('route_id'))

        # if code is not None:
        #     qrcode: QrCode = None
        #     try:
        #         qrcode: QrCode = QrCode.objects.get(stop_code=code)
        #     except QrCode.DoesNotExist:
        #         return Trip.objects.none()
        #     sequence: BaseManager = Stop_times.objects.filter(stop_id=qrcode.stop_id)
        #     queryset = queryset.filter(trip_id__in=sequence.values_list('trip_id'))

        return queryset


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
        # get real col names and stuff
        TRIP_ID_COL = StopTimes._meta.get_field("trip_id").column
        STOP_ID_COL = StopTimes._meta.get_field("stop_id").column
        STOPTIMES_TABLE = StopTimes._meta.db_table

        queryset = StopTimes.objects.all().order_by("trip_id")
        query = f"SELECT * FROM {STOPTIMES_TABLE} ORDER BY {TRIP_ID_COL}"

        # increase performance if no need to raw query
        raw_filter_used = False

        # stop_id
        stop_id = self.request.query_params.get("stop_id")
        if stop_id is not None:
            stop_id = stop_id.split(",")
            query = qu.q_col_in(
                select="*",
                from_target=STOPTIMES_TABLE,
                target_is_query=False,
                where_col_in={STOP_ID_COL: stop_id},
                order_by=TRIP_ID_COL,
            )
            raw_filter_used = True

        # get stop_id_all
        stop_id__all = self.request.query_params.get("stop_id__all")
        if stop_id__all is not None:
            stop_id__all = self.request.query_params.get("stop_id__all")
            stop_id__all = stop_id__all.split(",")
            query = qu.q_cols_match_all(
                table=STOPTIMES_TABLE,
                unique_cols=[TRIP_ID_COL, STOP_ID_COL],
                col_in={STOP_ID_COL: stop_id__all},
                col_match_all=[TRIP_ID_COL]
            )
            raw_filter_used = True

        # trip_id
        trip_id = self.request.query_params.get("trip_id")
        if trip_id is not None:
            trip_id = trip_id.split(",")

            if raw_filter_used:
                query = qu.q_col_in(
                    select="*",
                    from_target=query,
                    where_col_in={TRIP_ID_COL: trip_id},
                    order_by=TRIP_ID_COL,
                )
            else:
                queryset = queryset.filter(trip_id__in=trip_id).order_by("trip_id")

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
