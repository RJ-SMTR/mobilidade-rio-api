from mobilidade_rio.pontos.models import *

def stoptimes_child_or_parent(queryset, stop_id, raw_filter_used=False):
    """
    Filter stoptimes queryset to only include records where either:
    - location_type is 1 (station, stop parent) and stop_id matches provided stop_oid
    - location_type is 0, None (platform, stop child) and parent_station matches provided stop_oid

    Args:
        queryset (QuerySet): A queryset of GTFS stoptimes records to filter.
        stop_id (str): The GTFS ID of the stop or parent station to match.

    Returns:
        QuerySet: A filtered queryset of stoptimes records that match the provided stop_id or its parent station.
    """
    stop_id = stop_id if isinstance(stop_id, (list,tuple)) else [stop_id]
    # filter location_type
    location_type = Stops.objects.filter(
        stop_id__in=stop_id).values_list("location_type", flat=True)
    # get real col names and stuff
    STOP_ID_COL = StopTimes._meta.get_field("stop_id").column
    PARENT_STATION__STOPS = Stops._meta.get_field("parent_station").column
    # prevent error on searching inexistent stop_id
    # TODO: filter stop_id or children individually
    if len(location_type):
        # if stop is parent (station), return its children
        if location_type[0] == 1:
            if raw_filter_used:
                query = f"""
                SELECT * FROM ({queryset.query}) AS {qu.q_random_hash()}
                WHERE {STOP_ID_COL} IN (
                    SELECT stop_id FROM pontos_stops
                    WHERE {PARENT_STATION__STOPS} IN ({str(list(stop_id))[1:-1]})
                )
                """
                queryset = queryset.model.objects.raw(query, queryset.params)
            else:
                queryset = queryset.filter(
                    stop_id__in=Stops.objects.filter(
                        parent_station__in=stop_id).values_list("stop_id", flat=True)
                )
        # if stop is child (platform), return searched stops
        if location_type[0] == 0:
            if raw_filter_used:
                query = f"""
                SELECT * FROM ({queryset.query}) AS {qu.q_random_hash()}
                WHERE {STOP_ID_COL} IN ({str(list(stop_id))[1:-1]})
                """
                queryset = queryset.model.objects.raw(query, queryset.params)
            else:
                queryset = queryset.filter(stop_id__in=stop_id)
    return queryset

