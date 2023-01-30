"""Tasks for django-q"""

from datetime import datetime, timedelta
import pandas as pd

from mobilidade_rio.predictor.utils import *

def print_hello():
    """Print to test django-q"""
    print(f"Hello from django-q {datetime.now()}")


# TODO: Decide if this function will recall itself every 20 seconds 3x or if apps.py will do it.
def generate_prediction():
    """
    Update the prediction table.

    How will it be used:
    ---
    The app will call this function every N seconds to show to the user  
    the vehicles that arrives the fastest to the stop destiny.

    Return:
    ---
    One prediction of arrival time for each vehicle (not trip, not stop, the vehicle itself).  

    How it works:
    ---
    1. Get `real time` data and filter it according to the time limit and the day of the week
    2. Get first segment (e.g. stop1 - stop2) of each trip and calculate the distance between the start and end point.
    3. Get median model for the day of the week and hour
    """

    print("[GENPRED] etapa 1")
    # Etapa 1 - Obter os dados de tempo real
    # e filtrar os dados de acordo com o tempo limite e o dia da semana
    date=datetime.now()
    date_limit = date - timedelta(seconds=60)  
    weekday = {0: "U", 1: "U", 2: "U", 3: "U", 4: "U", 5: "S", 6: "D"}[date_limit.weekday()]

    real_time = get_realtime()
    real_time.dropna(subset=['dataHora','latitude','longitude','trip_short_name','direction_id','service_id'],inplace=True)
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
    first_segment = swst.copy()
    first_segment=get_current_stop(real_time,first_segment)

    hour = date_limit.hour

    #TODO:verificar se a tabela no original será alterada.
    median_model=MedianModel.objects.filter(tipo_dia=date_limit.weekday())
    median_model=median_model.filter(hora=hour)
    median_model = pd.DataFrame(list(median_model.values()))

    # Etapa 3 - substitui os elementos respectivos de swst com firt segment
    swst = swst[swst['stop_id'].isna()==False]
    swst=swst.merge(first_segment[['codigo','trip_id','shape_dist_traveled']], how='left', on=['trip_id','shape_dist_traveled'])
    swst['arrival_time']=swst.apply(lambda x: get_prediction(x,date_limit.weekday(),hour,median_model), axis=1)
    swst['dataHora']=date
    df_prediction = swst[['trip_id','stop_id','codigo','latitude','longitude','dataHora','trip_short_name','direction_id','service_id','stop_sequence','arrival_time']].copy()
    df_prediction = df_prediction.rename(columns={'codigo': 'id_veiculo'})

    print("[GENPRED] 3.7 insert", df_prediction.head(2).to_dict('records'))
    for row in df_prediction.to_dict('records'):
        Prediction.objects.update_or_create(**row)
    print("[GENPRED] end")

