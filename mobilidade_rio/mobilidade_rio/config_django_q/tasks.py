"""Tasks for django-q"""

from datetime import datetime, timedelta
import pandas as pd

from mobilidade_rio.predictor.utils import *

def print_hello():
    """Print to test django-q"""
    print(f"Hello from django-q {datetime.now()}")

# TODO: function workaround



def generate_prediction():

    print("[GENPRED] etapa 1")
    # Etapa 1 - Obter os dados de tempo real
    # e filtrar os dados de acordo com o tempo limite e o dia da semana
    date=datetime.now()
    date_limit = date - timedelta(seconds=60)  
    weekday = {0: "U", 1: "U", 2: "U", 3: "U", 4: "U", 5: "S", 6: "D"}[date_limit.weekday()]

    print("[GENPRED] 1.1")
    real_time = get_realtime()
    real_time.dropna(subset=['dataHora','latitude','longitude','trip_short_name','direction_id','service_id'],inplace=True)
    real_time = real_time.loc[real_time['dataHora'] > date_limit]
    real_time = real_time.loc[real_time['service_id']==weekday]


    print("[GENPRED] 1.2")
    trips = real_time.copy()
    trips.drop_duplicates(subset=['trip_short_name','service_id'],inplace=True)
    trips =trips['trip_short_name'].unique().tolist()

    print("[GENPRED] 1.3")
    swst = ShapesWithStops.objects.filter(trip_short_name__in=trips).order_by('shape_dist_traveled')
    print("[GENPRED] 1.3.1")
    # swst = swst.loc[swst['service_id']==weekday]
    print("[GENPRED] 1.3.2")
    swst = swst.filter(service_id=weekday)
    print("[GENPRED] 1.3.3")
    swst = pd.DataFrame(list(swst.values()))
    print(swst.info())
    print("[GENPRED] 1.3.4")
    swst = swst.astype({'direction_id':'int64','trip_short_name':'string'})
    print("[GENPRED] 1.3.5")

    print("[GENPRED] etapa 2")
    # Etapa 2 - Obter o primeiro segmento de cada viagem
    # e calcular a distância entre o ponto de partida e o ponto de chegada
    first_segment = swst.copy()
    first_segment=get_current_stop(real_time,first_segment)

    hour = date_limit.hour

    #TODO:verificar se a tabela no original será alterada.
    median_model=MedianModel.objects.filter(tipo_dia=date_limit.weekday())
    median_model=median_model.filter(hora=hour)
    median_model = pd.DataFrame(list(median_model.values()))

    print("[GENPRED] etapa 3")
    # Etapa 3 - substitui os elementos respectivos de swst com firt segment
    swst = swst[swst['stop_id'].isna()==False]

    swst=swst.merge(first_segment[['codigo','trip_id','shape_dist_traveled']], how='left', on=['trip_id','shape_dist_traveled'])

    swst['arrival_time']=swst.apply(lambda x: get_prediction(x,date_limit.weekday(),hour,median_model), axis=1)


    swst['dataHora']=date
    print("OK?", swst['arrival_time'].count())
    df_prediction = swst[['trip_id','stop_id','codigo','latitude','longitude','dataHora','trip_short_name','direction_id','service_id','stop_sequence','arrival_time']].copy()
    df_prediction = df_prediction.rename({'codigo': 'id_veiculo'}, inplace=True)
    print(df_prediction.info())

    print("[GENPRED] insert")
    print(df_prediction.head(2).to_dict('records'))
    for row in df_prediction.to_dict('records'):
        Prediction.objects.update_or_create(**row)
    print("[GENPRED] end")

