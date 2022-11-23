#from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from mobilidade_rio.predictor.models import *
from mobilidade_rio.predictor.serializers import *
import mobilidade_rio.pontos.models as gtfs_models
from django.db import connection
# import APIView
from rest_framework.views import APIView


class ShapeWithStopsView(APIView):

    def get(self, request):
        shapes_name = gtfs_models.Shapes.objects.model._meta.db_table
        stops_name = gtfs_models.Stops.objects.model._meta.db_table

        # exclude null cols (or with same name as its collumn)
        shapes_cols = [col.name for col in gtfs_models.Shapes.objects.model._meta.get_fields()]
        stops_cols = [col.name for col in gtfs_models.Stops.objects.model._meta.get_fields()]
        shape_with_stops_cols = list(set(["shape_pt_lat", "shape_pt_lon", "stop_lat", "stop_lon"]))
        q_row_ne_col_name = [f"{col} != '{col}'" for col in shape_with_stops_cols if col != 'id']
        q_row_ne_col_name = 'AND '.join(q_row_ne_col_name)

        
        # join shapes with stops
        # q_join_shapes_stops = f"""
        # select count (*) from (SELECT * FROM pontos_shapes INNER JOIN pontos_stops ON pontos_shapes.shape_pt_sequence < 100) as q
        # """

        # show stops where lat and lon are equal +- 0.0001 compared to shapes, using join
        offset = 0.00001
        q_shapes_stops_pos = f"""
        SELECT * FROM {stops_name} INNER JOIN {shapes_name} ON
        {q_row_ne_col_name}
        -- AND CAST({shapes_name}.shape_pt_lat AS DECIMAL(10,6)) = CAST({stops_name}.stop_lat AS DECIMAL(10,6))
        -- AND CAST({shapes_name}.shape_pt_lon AS DECIMAL(10,6)) = CAST({stops_name}.stop_lon AS DECIMAL(10,6))
        -- {q_row_ne_col_name}
        AND ABS(CAST({shapes_name}.shape_pt_lat AS DECIMAL(10,6)) - CAST({stops_name}.stop_lat AS DECIMAL(10,6))) < {offset}
        AND ABS(CAST({shapes_name}.shape_pt_lon AS DECIMAL(10,6)) - CAST({stops_name}.stop_lon AS DECIMAL(10,6))) < {offset}
        """

        # q_shapes_stops_pos = f"""
        # SELECT * FROM {stops_name}, {shapes_name}
        # -- WHERE {shapes_name}.shape_pt_lat IS NOT NULL AND {shapes_name}.shape_pt_lon IS NOT NULL
        # -- AND {stops_name}.stop_lat IS NOT NULL AND {stops_name}.stop_lon IS NOT NULL
        # WHERE {q_row_ne_col_name}
        # AND ABS(CAST({shapes_name}.shape_pt_lat AS DECIMAL(10,6)) - CAST({stops_name}.stop_lat AS DECIMAL(10,6))) < {offset}
        # AND ABS(CAST({shapes_name}.shape_pt_lon AS DECIMAL(10,6)) - CAST({stops_name}.stop_lon AS DECIMAL(10,6))) < {offset}
        # """

        q_shapes_stops = f"""
        SELECT * FROM {shapes_name}, {stops_name}
        """

        q_limit = f"""
        {q_shapes_stops_pos} LIMIT 20
        """

        q_count = f"""
        SELECT COUNT(*) FROM {shapes_name}
        """

        # count total number of rows in the table 

        
        with connection.cursor() as cursor:
            # print("[TESTING]")
            cursor.execute(q_shapes_stops_pos)
            # row = [dict(zip([key[0] for key in cursor.description], row))
            #        for row in cursor.fetchall()]
            row = cursor.fetchall()
            print(row)
            return Response(row)
            # print(row)
            # convert the list to dict, corresponding to ShapeWithStops model
            print("[COUNTING]")
            cursor.execute(q_count)
            count = cursor.fetchone()[0]
            print(count)

            # print
            shape_with_stops_cols = ShapeWithStops._meta.get_fields()


            return Response(row)
        # return json response
        # return Response({'get': 'query'})
        # return Response(query)


class ShapeWithStopsViewSet(viewsets.ModelViewSet):
    serializer_class = ShapeWithStopsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ShapeWithStops.objects.all().order_by("trip_id")

    # return query from get, not queryset
    

    def get_queryset(self):
        # create ShapeWithStops with false values
        # ShapeWithStops.objects.create(trip_id=1, shape_id=1, shape_pt_lat=1, shape_pt_lon=1, shape_pt_sequence=1, stop_id=1, stop_name=1, stop_lat=1, stop_lon=1)
        # queryset = ShapeWithStops.objects.all().order_by("trip_id")
        shapes_model_name = gtfs_models.Shapes.objects.model._meta.db_table
        stops_model_name = gtfs_models.Stops.objects.model._meta.db_table

        shapes_cols = [col.name for col in gtfs_models.Shapes.objects.model._meta.get_fields()]
        stops_cols = [col.name for col in gtfs_models.Stops.objects.model._meta.get_fields()]
        shape_with_stops_cols = [col.name for col in ShapeWithStops.objects.model._meta.get_fields()]
        # exclude cols if not in  shapes or stops but mantain pk
        shape_with_stops_cols = [col for col in shape_with_stops_cols
                                 if col in shapes_cols or col in stops_cols or col == 'id']
        # select shapes, stops and select id of shapes as id
        q_row_ne_col_name = [f"{col} != '{col}'" for col in shape_with_stops_cols if col != 'id']
        q_row_ne_col_name = 'AND '.join(q_row_ne_col_name)
        q_shapes_stops = f"""
        SELECT {', '.join(shape_with_stops_cols)}
        FROM {shapes_model_name}, {stops_model_name}
        WHERE {q_row_ne_col_name}
        LIMIT 10
        """
        
        query = q_shapes_stops

        print("[LOG] query: ", query)
        queryset = ShapeWithStops.objects.raw(query)
        if not queryset:
            # return empty queryset
            queryset = ShapeWithStops.objects.none()
        
        # print query result
        print("[LOG] queryset: ", queryset)
        return queryset
        # queryset that is literally shapes + stops
        stop_id = None
        # get stop_id from query params
        if 'stop_id' in self.request.query_params:
            stop_id = self.request.query_params.get('stop_id')

        if stop_id is not None and len(stop_id):
            # get multiple stop_ids

            # variables
            stop_ids = stop_id.split(",")
            stop_ids_formatted = tuple(stop_ids)
            if len(stop_ids) == 1:
                stop_ids_formatted = f"('{stop_id}')"

            # get shapes model name in db

            # return cols of shapes + stops
            query = f"""
            SELECT * FROM {shapes_model_name}, {stops_model_name}

            """

            # execute query
            # queryset = queryset.raw(query)
        return queryset

class PredictorViewSet(viewsets.ModelViewSet):
    pass