"""Tasks for django-q"""

from datetime import datetime, timedelta
import pandas as pd

from mobilidade_rio.predictor.utils import *

def print_hello():
    """Print to test django-q"""
    print(f"Hello from django-q {datetime.now()}")


def generate_prediction():

    # Etapa 1 - Obter os dados de tempo real
    # e filtrar os dados de acordo com o tempo limite e o dia da semana
    date_now=datetime.now()
    date_limit = date_now - timedelta(seconds=60)
    weekday = {0: "U", 1: "U", 2: "U", 3: "U", 4: "U", 5: "S", 6: "D"}[date_limit.weekday()]

    real_time = get_realtime()
    real_time.dropna(subset=[
        'dataHora','latitude','longitude','trip_short_name','direction_id','service_id'
        ],inplace=True)
    real_time = real_time.loc[real_time['dataHora'] > date_limit]
    real_time = real_time.loc[real_time['service_id']==weekday]

    trips = real_time.copy()
    trips.drop_duplicates(subset=['trip_short_name','service_id'],inplace=True)
    trips =trips['trip_short_name'].unique().tolist()

    swst = ShapesWithStops.objects.filter(trip_short_name__in=trips).order_by('shape_dist_traveled')
    # swst = swst.loc[swst['service_id']==weekday]
    swst = swst.filter(service_id=weekday)
    swst = pd.DataFrame.from_records(swst.values())
    swst = swst.astype({'direction_id':'int64','trip_short_name':'string'})


    # Etapa 2 - Obter o primeiro segmento de cada viagem
    # e calcular a distância entre o ponto de partida e o ponto de chegada
    first_trip_segment = swst.copy()
    first_trip_segment=get_current_stop(real_time,first_trip_segment)

    hour = date_limit.hour

    #TODO:verificar se tipo_dia na tabela no original será alterada.
    median_model = MedianModel.objects.filter(tipo_dia=date_limit.weekday()+1)
    median_model = median_model.filter(hora=hour)  # hora 1-7
    median_model = pd.DataFrame.from_records(median_model.values())


    # Etapa 3 - Obtém predição usando swst trocando por valores em first_trip_segment
    swst = swst[swst['stop_id'].notna()]

    pred = swst.merge(
        first_trip_segment[['codigo','trip_id','shape_dist_traveled']],
        how='left',
        on=['trip_id','shape_dist_traveled']
        )

    pred['arrival_time']=pred.apply(
        lambda x: get_prediction(x,date_limit.weekday(),hour,median_model,swst),
        axis=1
        )

    pred['dataHora'] = date_now

    # Predictor
    pred = pred[[
        'trip_id',
        'stop_id',
        'codigo',
        'latitude',
        'longitude',
        'dataHora',
        'trip_short_name',
        'direction_id',
        'service_id',
        'arrival_time'
        ]].copy()

    pred = pred.rename(columns={'codigo': 'id_veiculo'})
    pred['id_veiculo'] = pred['id_veiculo'].replace({np.nan: None})

    pred = pred.astype({
        "trip_id":"string",
        "stop_id":"string",
        "id_veiculo":"string",
        "dataHora":"string",
        "trip_short_name":"string",
        "direction_id":"string",
        "service_id":"string",
        "arrival_time":'object'
        })

    for row in pred.to_dict('records'):
        Prediction.objects.update_or_create(**row)
