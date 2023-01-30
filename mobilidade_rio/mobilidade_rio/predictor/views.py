#from django.shortcuts import render
from rest_framework import viewsets
from mobilidade_rio.predictor.models import *
from mobilidade_rio.predictor.serializers import *
# import APIView


class PredictorViewSet(viewsets.ModelViewSet):
    """
    Obter previsão de chegada de **veículos** (trips) e **paradas de ônibus** (stops)

    Parâmetros:
    ---
    - trip_name:
        - Pesquisar parte do nome do veículo (`trip_short_name`)
    - stop_id
        - Pesquisar pelo id da parada
    """

    def get_queryset(self):
        queryset = Prediction.objects.all().order_by("dataHora","trip_short_name", "stop_id")

        # filtrar por trip_name (trip_short_name)
        trip_name = self.request.query_params.get("trip_name")
        if trip_name:
            trip_name = trip_name.split(",")
            queryset = queryset.filter(trip_short_name__in=trip_name)

        # calcular tempo de viagem até stop_id_destiny
        stop_id_destiny = self.request.query_params.get("stop_id_destiny")
        if stop_id_destiny:
            # 1.ordenando por 
            stop_id_destiny = stop_id_destiny.split(",")
            # queryset = queryset.filter(stop_id__in=stop_id_destiny)

        

        return queryset
