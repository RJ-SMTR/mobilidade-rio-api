import json
import requests as r

from rest_framework.serializers import Serializer
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework import permissions
from rest_framework.response import Response

from mobilidade_rio.predictor.models import *
from mobilidade_rio.predictor.serializers import *
import mobilidade_rio.pontos.models as gtfs_models
from django.db import connection
import mobilidade_rio.predictor.utils


#from rest_framework.generics import APIView

from mobilidade_rio.__init__ import predictor
import pandas as pd

#http://localhost:8010/predictor/pred/
class PredictorView(APIView):
    
    def get(self, request):
        #?trip_name=22,41,50&stop_id=4128BC0005U2
        #all_next_stops = pd.DataFrame()

        # Pegar realtime do servidor do realtime
        url=os.environ.get('API_REAL_TIME')
        x=r.get(url)
        real_time = pd.read_json(x.text)
        real_time["comunicacao"] = real_time["comunicacao"].apply(datetime.fromtimestamp)
        real_time["inicio_viagem"] = real_time["inicio_viagem"].apply(datetime.fromtimestamp)

        # Filtar por trip em swst, realtime and MedianModel
        trip_short_name_list = self.request.query_params.get('trip_name', None)
        if trip_short_name_list:
            trip_short_name_list = trip_short_name_list.strip().split(",")

            # filtrar por trip_short_name
            real_time = real_time.loc[real_time["linha"].isin(trip_short_name_list)] #fim da 5

            # filtro em predictormodel
            modelo_mediana = MedianModel.objects.filter(trip_id__in=trip_short_name_list) # fim da 3
            modelo_mediana = pd.DataFrame(list(modelo_mediana.values()))

            #self.self.trip_stops e --> swst
            swst = ShapeWithStops.objects.filter(trip_id__in=trip_short_name_list)
            swst = pd.DataFrame(list(swst.values()))
            trip_id = swst[["trip_id","trip_short_name","direction_id"]].dropna().drop_duplicates()
            # Seria bom se quando gerar o swst já trocar o 0/1 por I/V adequando o ao modelo da realtime.

        else:
            #caso não tenha trip para filtrar.
            modelo = MedianModel.objects.all()
            modelo_mediana = pd.DataFrame(list(modelo_mediana.values()))

            swst = ShapeWithStops.objects.all()
            swst = pd.DataFrame(list(swst.values()))
            #validar a necessidade do direction uma vez que temos trip_id
            trip_id = swst[["trip_id","trip_short_name","direction_id"]].dropna().drop_duplicates()

        #passo 6.1
        lista_predicoes = real_time.apply(utils.predict_individual_arrivals, axis=1).values
        predicoes = pd.concat(lista_predicoes, ignore_index=True)

           
    
        
        if stop_list:
            pred = pred[["trip_id","chegada", "stop_id","bus_id"]].loc[pred['stop_id'].isin(stop_list)]
        else:
            pred = pred[["trip_id","chegada", "stop_id","bus_id"]]
 
        return Response(json.loads(pred.to_json(orient="records")))
    
            # filter by stops
        stop_list = self.request.query_params.get('stop_id', None)
        if stop_list:
            stop_list = stop_list.strip().split(",")
            # TODO: filter by stop_id


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

        #print("[LOG] query: ", query)
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
    
