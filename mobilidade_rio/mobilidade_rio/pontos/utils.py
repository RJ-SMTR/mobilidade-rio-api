"""utils.py - Utils for pontos app"""

from mobilidade_rio.pontos.models import *
from django.db.models.query import QuerySet
import mobilidade_rio.utils.query_utils as qu
import mobilidade_rio.utils.django_utils as du


def q_stoptimes__stop_id(stop_id=None, query=None, select=("*")):
    """
    Filter stop by stop_id
    If stop is parent_station, filter by its children

    Args:
        query (QuerySet|str): QuerySet to filter
        stop_id (str): stop_id to filter

    Returns:
        query = <queryset>:
            QuerySet filtered by stop_id or children
        query = <str>:
            SQL query filtered by stop_id or children

    """

    # validade stop_id
    if stop_id is None:
        stop_id = ()

    # filter location_type
    location_type = Stops.objects.filter(
        stop_id__in=stop_id).values_list("location_type", flat=True)

    # validate query
    raw_filter_used = isinstance(query, QuerySet) is False

    # prevent error on searching inexistent stop_id
    # TODO: filter stop_id or children individually
    if len(location_type):
        # validate query
        if query is None:
            query = du.get_table(StopTimes)
        elif isinstance(query, str):
            query = f"({query}) AS {qu.q_random_hash()}"

        # if station is parent_station, return children
        if location_type[0] == 1:
            if raw_filter_used:
                query = f"""
                SELECT {','.join(select)}
                FROM {query}
                WHERE {du.get_col(StopTimes, 'stop_id')} IN (
                    SELECT stop_id FROM pontos_stops
                    WHERE {du.get_col(Stops, 'parent_station')} IN ({str(list(stop_id))[1:-1]})
                )
                """
            else:
                query = query.filter(
                    stop_id__in=Stops.objects.filter(
                        parent_station__in=stop_id).values_list("stop_id", flat=True)
                )
        # if first stop has no child (location_type = 0|None), return searched stations
        else:
            if raw_filter_used:
                query = f"""
                SELECT {','.join(select)}
                FROM {query}
                WHERE {du.get_col(StopTimes, 'stop_id')} IN ({str(list(stop_id))[1:-1]})
                """
            else:
                query = query.filter(stop_id__in=stop_id)

    elif query is None:
        query = StopTimes.objects.all().order_by("trip_id")

    return query

def get_extra_stops_cols(table_name, return_type="list"):
    """
    Create extra columns for stoptimes
    This function is part of in q_stops_prev_next()
        because it can be better to maintain and optimize
    """
    ret = [
        f"""
            (
                SELECT stop_id_id
                FROM pontos_stoptimes
                WHERE trip_id_id = {table_name}.trip_id_id
                    AND stop_sequence < {table_name}.stop_sequence
                LIMIT 1
            ) AS previous_stop_id
        """,
        f"""
            (
                SELECT stop_name FROM pontos_stoptimes
                JOIN pontos_stops ON pontos_stoptimes.stop_id_id = pontos_stops.stop_id
                WHERE trip_id_id = {table_name}.trip_id_id
                    AND stop_sequence < {table_name}.stop_sequence
                LIMIT 1
            ) AS previous_stop_name
        """,
        f"""
            (
                SELECT stop_id_id
                FROM pontos_stoptimes
                WHERE trip_id_id = {table_name}.trip_id_id
                    AND stop_sequence > {table_name}.stop_sequence
                ORDER BY stop_sequence
                LIMIT 1
            ) AS next_stop_id
        """,
        f"""
            (
                SELECT stop_name FROM pontos_stoptimes
                JOIN pontos_stops ON pontos_stoptimes.stop_id_id = pontos_stops.stop_id
                WHERE trip_id_id = {table_name}.trip_id_id
                    AND stop_sequence > {table_name}.stop_sequence
                ORDER BY stop_sequence
                LIMIT 1
            ) AS next_stop_name
        """,
        f"""
            (
                SELECT stop_sequence
                FROM pontos_stoptimes
                WHERE trip_id_id = {table_name}.trip_id_id
                    AND stop_sequence < {table_name}.stop_sequence
                LIMIT 1
            ) AS previous_stop_sequence
        """,
        f"""
            (
                SELECT stop_sequence
                FROM pontos_stoptimes
                WHERE trip_id_id = {table_name}.trip_id_id
                    AND stop_sequence > {table_name}.stop_sequence
                ORDER BY stop_sequence
                LIMIT 1
            ) AS next_stop_sequence
        """
    ]
    if return_type == "list":
        return ret
    elif return_type == "str":
        return ", ".join(ret)


def q_stops_prev_next(
    select=("*"),
    table=StopTimes._meta.db_table,
    conditions="",
    order_by=("trip_id_id", "stop_sequence")
):
    """Get stops with previous and next stops"""
    return f"""
    SELECT {", ".join(select)},
        {get_extra_stops_cols("st", "str")}
    FROM {table} AS st
    {conditions}
    ORDER BY {", ".join(order_by)}
    """
