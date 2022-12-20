import json

from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response

from mobilidade_rio.predictor.models import *
from mobilidade_rio.predictor.serializers import *
import mobilidade_rio.pontos.models as gtfs_models
from django.db import connection


#from rest_framework.views import APIView

from mobilidade_rio.__init__ import predictor
import pandas as pd

#http://localhost:8010/predictor/pred/?trip_names=22,41,50&stops=4128BC0005U2,4128BO0017U2
class PredictorView(APIView):
    def get(self, request):
        all_next_stops = pd.DataFrame()
        stop_list = []
        trip_short_name_list = []
        has_trip = request.GET.get('trip_names', '')!=''
        has_stop = request.GET.get('trip_names', '')!=''

        if has_trip:
            trip_short_name_list = request.GET.get('trip_names', '')
            trip_short_name_list = trip_short_name_list.strip().split(",")
            
        if has_stop:
            stop_list = request.GET.get('stops', '')
            stop_list = stop_list.strip().split(",")

        predictor.capture_real_time_data(trip_short_name_list,has_trip)
        pred = predictor.predict_all_arrivals()
        if has_stop:
            pred = pred[["trip_id","chegada", "stop_id","bus_id"]].loc[pred['stop_id'].isin(stop_list)]
        else:
            pred = pred[["trip_id","chegada", "stop_id","bus_id"]]
 
        return Response(json.loads(pred.to_json(orient="records")))



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
    
