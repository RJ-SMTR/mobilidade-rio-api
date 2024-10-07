import logging
from typing import IO, List
from xml.dom import NotFoundErr
import geopy.distance
from django.db.models import QuerySet
from mobilidade_rio.pontos.models import (
    Agency,
    Calendar,
    CalendarDates,
    Frequencies,
    Routes,
    Shapes,
    StopTimes,
    Stops,
    Trips,
)

logger = logging.getLogger("pontos_utils")


def get_distance(p1: tuple, p2: tuple) -> float:
    return geopy.distance.great_circle(p1, p2).meters


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def stop_times_parent_or_child(
        stop_id: List[str],
        queryset: QuerySet = Frequencies.objects.all(  # pylint: disable=E1101
        ).order_by("trip_id"),
) -> QuerySet:
    """
    Filter by stop_id.

    If stop is parent_station, return results from its children;

    if not, return results from itself.
    """

    location_type = Stops.objects.filter(  # pylint: disable=E1101
        stop_id__in=stop_id).values_list("location_type", flat=True)

    # the first stop defines if all stops will be considered parent or child
    if location_type:

        # if stop is parent (station), return its children
        if location_type[0] == 1:
            queryset = queryset.filter(
                stop_id__in=Stops.objects.filter(  # pylint: disable=E1101
                    parent_station__in=stop_id).values_list("stop_id", flat=True)
            )

        # if stop is child (platform), return searched stops
        if location_type[0] == 0:
            queryset = queryset.filter(stop_id__in=stop_id)

    # otherwise, stop id not found
    else:
        queryset = queryset.none()

    return queryset
