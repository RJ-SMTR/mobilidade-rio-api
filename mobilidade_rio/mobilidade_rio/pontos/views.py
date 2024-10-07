"""
pontos.views - to serve API endpoints
"""

# stop_code
import datetime
import logging
import operator
from functools import reduce
from rest_framework import permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.request import Request

from mobilidade_rio.pontos.services import UploadGtfsService
from mobilidade_rio.pontos.models import *

from .paginations import LargePagination
from .serializers import *
from .utils import stop_times_parent_or_child

logger = logging.getLogger("pontos_views")


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

        # filter trip_short_name
        trip_short_name = self.request.query_params.get("trip_short_name")
        if trip_short_name is not None:
            trip_short_name = trip_short_name.split(',')
            queryset = queryset.filter(trip_short_name__in=trip_short_name)

        # filter direction_id
        direction_id = self.request.query_params.get("direction_id")
        if direction_id is not None:
            direction_id = direction_id.split(',')
            queryset = queryset.filter(direction_id__in=direction_id)

        # filter service_id
        service_id = self.request.query_params.get("service_id")
        if service_id is not None:
            service_id = service_id.split(',')
            queryset = queryset.filter(service_id__in=service_id)

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
            queryset = queryset.filter(
                shape_id__in=shape_id).order_by("shape_id")

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
            queryset = queryset.filter(
                stop_code__in=stop_code).order_by("stop_id")

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
        # trip_id_col = StopTimes._meta.get_field("trip_id").column
        # stop_id_col = StopTimes._meta.get_field("stop_id").column
        queryset = StopTimes.objects.all().order_by("trip_id", "stop_sequence")

        # add parameter to show all combinations (logical OR)
        show_all = self.request.query_params.get("show_all")

        # filter by unique trips combinations (default - logical AND)
        if not show_all:
            unique_trips_fields = [
                "trip_short_name",
                "direction_id",
                "service_id",
                "shape_id",
            ]
            order = [
                "trip_id",
                "trip_id__trip_short_name",
                "trip_id__direction_id",
                "trip_id__service_id",
                "trip_id__shape_id",
                "stop_sequence",
            ]
            unique_trips = Trips.objects.order_by(
                *unique_trips_fields).distinct(*unique_trips_fields)
            queryset = queryset.filter(
                trip_id__in=unique_trips).order_by(*order)

        # filter trip_id
        trip_id = self.request.query_params.get("trip_id")
        if trip_id is not None:
            trip_id = trip_id.split(',')
            queryset = queryset.filter(trip_id__in=trip_id)

        # filter trip_short_name
        trip_short_name = self.request.query_params.get("trip_short_name")
        if trip_short_name is not None:
            trip_short_name = trip_short_name.split(',')
            queryset = queryset.filter(
                trip_id__trip_short_name__in=trip_short_name)

        # filter direction_id
        direction_id = self.request.query_params.get("direction_id")
        if direction_id is not None:
            direction_id = direction_id.split(',')
            queryset = queryset.filter(trip_id__direction_id__in=direction_id)

        # filter service_id
        service_id = self.request.query_params.get("service_id")
        if service_id is not None:
            service_id = service_id.split(',')
            queryset = queryset.filter(trip_id__service_id__in=service_id)

        # filter stop_id
        stop_id = self.request.query_params.get("stop_id")
        if stop_id is not None:
            stop_id = stop_id.split(",")
            queryset = stop_times_parent_or_child(stop_id, queryset)

        # filter for trips passing by all given stops
        # query = queryset.query
        # raw_filter_used = False
        # stop_id__all = self.request.query_params.get("stop_id__all")
        # if stop_id__all is not None:
        #     stop_id__all = stop_id__all.split(",")
        #     query = qu.q_cols_match_all(
        #         table=query, table_is_query=True,
        #         unique_cols=[trip_id_col, stop_id_col],
        #         col_in={stop_id_col: stop_id__all},
        #         col_match_all=[trip_id_col],
        #     )
        #     raw_filter_used = True

        # execute query
        # if raw_filter_used:
        #     queryset = queryset.raw(query)

        return queryset


class FrequenciesViewSet(viewsets.ModelViewSet):

    """
    API endpoint to show frequencies data
    """

    serializer_class = FrequenciesSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = Frequencies.objects.all().order_by("id")

    def get_queryset(self):
        queryset = Frequencies.objects.all().order_by("id")

        # filter stop_id
        stop_id = self.request.query_params.get("stop_id")
        if stop_id is not None:
            stop_id = stop_id.split(",")

            # filter by stop_times
            stop_times = StopTimes.objects.all().order_by("trip_id", "stop_sequence")
            stop_times = stop_times_parent_or_child(stop_id, stop_times)
            stop_times_trip_id = list(
                stop_times.values_list("trip_id", flat=True))

            # filter frequencies by
            queryset = queryset.filter(trip_id__in=stop_times_trip_id)

        # filter trip_id
        trip_id = self.request.query_params.get("trip_id")
        if trip_id is not None:
            trip_id = trip_id.split(',')
            queryset = queryset.filter(trip_id__in=trip_id)

        # filter trip_short_name
        trip_short_name = self.request.query_params.get("trip_short_name")
        if trip_short_name is not None:
            trip_short_name = trip_short_name.split(',')
            queryset = queryset.filter(
                trip_id__trip_short_name__in=trip_short_name)

        # filter direction_id
        direction_id = self.request.query_params.get("direction_id")
        if direction_id is not None:
            direction_id = direction_id.split(',')
            queryset = queryset.filter(trip_id__direction_id__in=direction_id)

        # filter service_id
        service_id = self.request.query_params.get("service_id")
        if service_id is not None:
            service_id = service_id.split(',')
            queryset = queryset.filter(trip_id__service_id__in=service_id)

        return queryset


class UploadGtfsViewSet(viewsets.ViewSet):

    """
    Upload GTFS zip
    """

    serializer_class = UploadGtfsSerializer
    """"""
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def create(self, request: Request):
        """post"""
        # validate
        serializer = UploadGtfsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # parse
        user = request.user
        gtfs_zip = request.FILES.get("gtfs_zip", None)
        if gtfs_zip is None or gtfs_zip == '':
            return Response({
                "error": "gtfs_zip is mandatory",
                "timestamp": datetime.datetime.now()
            }, status=500)

        zip_files = [x for x in request.POST.get("zip_files", "").split(",") if x]

        return UploadGtfsService.upload_gtfs(user, gtfs_zip, zip_files)
