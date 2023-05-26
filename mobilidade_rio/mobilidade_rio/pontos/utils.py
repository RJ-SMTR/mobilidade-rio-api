import geopy.distance
from django.db.models import QuerySet
from mobilidade_rio.pontos.models import (
    StopTimes,
    Trips
)

def get_distance(p1: tuple, p2: tuple) -> float:
    return geopy.distance.great_circle(p1, p2).meters


def safe_cast(val, to_type, default=None):
    try:
        return to_type(val)
    except (ValueError, TypeError):
        return default


def stop_times_non_redundant_trips(
    queryset:QuerySet = StopTimes.objects.all().order_by("trip_id")
    ) -> QuerySet:
    """
    Filter ocourrences by items within trips with unique combinations.
    
    These non unique combinations are created to register variations of each trip in frequencies.
    
    ``queryset``(optional): StopTimes queryset to filter
    """

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
    unique_trips = Trips.objects.order_by(*unique_trips_fields).distinct(*unique_trips_fields)
    queryset = queryset.filter(trip_id__in=unique_trips).order_by(*order)

    return queryset