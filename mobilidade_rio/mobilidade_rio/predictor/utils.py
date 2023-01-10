"""utils.py - Utils for predictor app"""

from mobilidade_rio.utils import query_utils as qu
from mobilidade_rio.utils.django_utils import get_table, get_col, postgis_exists
from mobilidade_rio.pontos.utils import q_stoptimes__stop_id, q_stops_prev_next
from mobilidade_rio.pontos.models import *

def q_shapes_with_stops(
    stop_id : list = (''),
):
    """
    v2.1 - 2023/01/09
    Get stoptimes with its related shape and join with stops, routes and trips

    Args:
        stop_id: list of stop_ids to filter
            Default: None
        select_cols: list of columns to select
            Default: "*"

    How it works:
        1. Get stoptimes, join with trips, stops, routes, shapes
            In stoptimes:
                Get previous and next stop_id and stop_name from stoptimes
                Filter by stop_id using criterias in q_stops_prev_next()
        2. Get distance between shape and stop
            If postgis is enabled, use 3D distance
            Else, use 2D distance
        3. For each id__stoptimes, get the shape with the smallest distance
            Using DISTINCT and ORDER BY
    """

    distance = """
        ST_Distance(
            ST_MakePoint(shape_pt_lon, shape_pt_lat)::geography,
            ST_MakePoint(stop_lon, stop_lat)::geography
        )
    """ if postgis_exists() else """
        CAST(
            SQRT(
                POW(
                    CAST(shape_pt_lat AS DECIMAL(10,6))
                    - CAST(stop_lat AS DECIMAL(10,6))
                ,2)
                + POW(
                    CAST(shape_pt_lon AS DECIMAL(10,6))
                    - CAST(stop_lon AS DECIMAL(10,6))
                ,2)
            )
        AS DECIMAL(10,6))
    """

    return f"""
    SELECT DISTINCT ON (id__stoptimes) * FROM (
        SELECT
            -- select specific cols instead of * to avoid errors and save performance
            stoptimes.id,
            stoptimes.arrival_time,
            stoptimes.departure_time,
            stoptimes.stop_sequence,
            stoptimes.pickup_type,
            stoptimes.drop_off_type,
            shapes.shape_id,
            shapes.shape_dist_traveled,
            shapes.shape_pt_sequence,
            shapes.shape_pt_lat,
            shapes.shape_pt_lon,
            stops.stop_id,
            stops.stop_name,
            stops.stop_lat,
            stops.stop_lon,
            stops.stop_code,
            stops.stop_desc,
            stops.zone_id,
            stops.stop_url,
            stops.stop_timezone,
            stops.wheelchair_boarding,
            trips.trip_id,
            trips.trip_short_name,
            routes.route_id,
            routes.route_short_name,
            routes.route_long_name,

            stoptimes.id AS id__stoptimes,
            shapes.id AS id__shapes,

            {distance} AS distance

        FROM ({q_stoptimes__stop_id(
                stop_id=stop_id,
                query=q_stops_prev_next()
            )}) AS stoptimes
            JOIN {get_table(Trips)} trips ON trips.trip_id = {get_col(StopTimes, 'trip_id')}
            JOIN {get_table(Stops)} stops ON stoptimes.{get_col(StopTimes, 'stop_id')} = stops.stop_id
            JOIN {get_table(Routes)} routes ON trips.{get_col(Trips, 'route_id')} = routes.route_id
            JOIN {get_table(Shapes)} shapes ON trips.shape_id = shapes.shape_id
        ) AS {qu.q_random_hash()}
    ORDER BY id__stoptimes, distance
    """
