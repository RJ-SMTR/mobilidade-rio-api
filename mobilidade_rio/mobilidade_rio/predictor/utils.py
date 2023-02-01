
from datetime import datetime, timedelta
import json
import pandas as pd
import numpy as np
import requests
import os

from mobilidade_rio.predictor.models import *



def get_realtime():

    """
    Get realtime API data, filter and return a dataframe.

    Realtime API fields:
    ---
    - codigo
    - placa
    - linha
    - latitude
    - longitude
    - dataHora
    - velocidade
    - id_migracao_trajeto
    - sentido
    - trajeto
    - hodometro

    TODO: confirm if the fields are correct.
    """

    ret_data = {
        "code": 0,
        "status": "ok",
        "message": "",
    }

    # 1. Get realtime data from API
    url = os.environ.get('API_REALTIME')
    headers = os.environ.get('API_HEADER')
    headers = json.loads(headers)
    api_response = requests.get(url, headers=headers ,timeout=10)
    api_response =json.loads(api_response.text)
    df_realtime= pd.json_normalize(api_response['veiculos'])

    # Avoid warning 'json does not have iloc'
    df_realtime = pd.DataFrame(df_realtime)

    # 2. map direction, weekday; exclude old vehicles
    df_realtime.rename(columns={
        "sentido": "direction_id", "linha": "trip_short_name"}, inplace=True)

    # direction_id
    df_realtime["direction_id"] = df_realtime["direction_id"].map(
        {"ida": 0, "volta": 1})

    # weekend
    df_realtime["dataHora"] = (
        df_realtime["dataHora"] / 1000).apply(datetime.fromtimestamp)
    print("GR 2.1 df_realtime:", df_realtime.head(5))

    # Excluir veículos mais antigos que 20s
    df_realtime = df_realtime[df_realtime["dataHora"]
                              > (datetime.now() - timedelta(seconds=20))]
    if df_realtime.empty:
        ret_data["message"] = "[get_realtime error] no vehicles in the last 20s."
        ret_data["code"] = 1
        ret_data["status"] = "err_vehicle_20s"
        return df_realtime, ret_data

    # TODO: Confirmar se o map {5:"S",6:"D"} está correto.
    df_realtime["service_id"] = df_realtime["dataHora"].dt.weekday.map(
        {0: "U", 1: "U", 2: "U", 3: "U", 4: "U", 5: "S", 6: "D"})

    return df_realtime, ret_data


def _haversine_np(lat1,lon1,lat2, lon2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """

    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Retorna NaN para todo
    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c

    return km


def get_current_stop(positions, shapes):
    """
    1. Identifica trip_id
    2. Identifica ponto origem, ponto destino (em relação ao veículo)
    """

    positions=positions.astype({'direction_id':'int64','trip_short_name':'string'})
    shapes= shapes.astype({'direction_id':'int64','trip_short_name':'string'})
    positions.rename(columns={"latitude":"registro_lat","longitude":"registro_lon"}, inplace=True)
    positions = positions.merge(shapes, on=["trip_short_name","direction_id","service_id"],how='right')
    positions['distance']=positions.apply(lambda row: _haversine_np(row['registro_lat'], row['registro_lon'], row['latitude'], row['longitude']), axis=1)
    bestidxs=positions.dropna(subset=['distance']).sort_values(by=["distance"])
    bestidxs.drop_duplicates(subset=['codigo'],inplace=True, keep='first')
    return bestidxs[['trip_id','stop_id','next_stop_id','previous_stop_id','shape_dist_traveled','codigo','trip_short_name', 'direction_id', 'dataHora']]


def get_prediction(row,dia_da_semana,hora_atual,modelo_mediana,swst):
    """ Calculates de residual distance and returns prediction of current section using the model """

    stop_id_origem = row['previous_stop_id']
    stop_id_destino = row['next_stop_id']

    if stop_id_origem == None :
        return None
    if stop_id_destino == None :
        return None

    prediction=pd.DataFrame()
    try:
        prediction = modelo_mediana[
            (modelo_mediana.stop_id_origin == stop_id_origem) &
            (modelo_mediana.stop_id_destiny == stop_id_destino) &
            (modelo_mediana.tipo_dia == dia_da_semana) &
            (modelo_mediana.hora == hora_atual)
        ]["delta_secs"]
    except Exception:
        print(stop_id_origem, modelo_mediana.info())


    if prediction.empty:
        return None
    prediction = prediction.squeeze()

    # Se existe um carro, calculamos o residual.
    if row['codigo']:
        next_stop_distance = swst[
        (swst['stop_id'] == stop_id_destino) &
        (swst['trip_id'] == row['trip_id'])]["shape_dist_traveled"].squeeze()

        # verificando se denominador é um número e diferente de zero.
        if next_stop_distance and next_stop_distance != 0:
            residual_distance = (next_stop_distance - row["shape_dist_traveled"]) / next_stop_distance
        else:
            return None

        return timedelta(seconds=prediction*residual_distance)

    # se não um carro, predição do tempo entre stop next - stop current.
    else:
        return timedelta(seconds=prediction)
