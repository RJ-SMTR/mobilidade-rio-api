from rest_framework import viewsets
from mobilidade_rio.predictor.models import Prediction
from mobilidade_rio.predictor.serializers import PredictionSerializer
import django.db.models as dm
import pandas as pd


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

    serializer_class = PredictionSerializer

    def get_queryset(self):
        queryset = Prediction.objects.all().order_by(
            "dataHora", "trip_short_name", "stop_id")

        # filtrar por trip_name (trip_short_name)
        trip_name = self.request.query_params.get("trip_name")
        if trip_name:
            trip_name = trip_name.split(",")
            queryset = queryset.filter(trip_short_name__in=trip_name)

        # calcular tempo de viagem até stop_id_destiny
        stop_id_destiny = self.request.query_params.get("stop_id_destiny")
        if stop_id_destiny:
            stop_id_destiny = stop_id_destiny.split(",")
            # TODO: 1. Order by stop_sequence (doesn't exist)
            #       Solutions: create col; order by pk (need rewrite tasks.py?)
            # queryset = queryset.order_by("pk")
            # 2. Selecionar da linha que contém id_veiculo
            vehicles = queryset.filter(id_veiculo__isnull=False, arrival_time__isnull=False)
            # # 3. Para cada veículo, selecionar paradas posteriores e somar arrival_time
            df_vehicles = pd.DataFrame.from_records(vehicles.values())
            for i, vehicle in enumerate(vehicles):
                after_vehicle = queryset.filter(
                    pk__gt=vehicle.pk, trip_id=vehicle.trip_id, arrival_time__isnull=False)
                sum_after = list(after_vehicle.aggregate(dm.Sum("arrival_time")).values())[0]
                df_vehicles.loc[i, "arrival_time"] = vehicle.arrival_time + sum_after
            queryset = [dict(zip([col for col in df_vehicles], row)) for row in df_vehicles.values]

        return queryset
