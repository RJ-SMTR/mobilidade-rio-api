import os
import requests
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def get_realtime(df_realtime: pd.DataFrame):
    """
    Get realtime API data, filter and return a dataframe.

    Parameters
    ----------
    df_realtime
        Dataframe with realtime data
    """

    # 1. Get realtime data from API

    # TODO: trocar link da API por login do vault para obter URL
    # Está configurado para rodar na API antiga, portanto não vai funcionar até pegar a nova.

    url = os.environ.get('API_REALTIME')
    api_response = requests.get(url, timeout=10)
    df_realtime = pd.read_json(api_response.text)
    # Avoid warning 'json does not have iloc'
    df_realtime = pd.DataFrame(df_realtime)

    # 2. map direction, weekday; exclude old vehicles
    df_realtime.rename(columns={
        "sentido": "direction_id", "linha": "trip_short_name"}, inplace=True)
    # direction_id
    df_realtime["direction_id"] = df_realtime["direction_id"].map({"ida": 0, "volta": 1})

    # weekend
    df_realtime["dataHora"] = (df_realtime["dataHora"] / 1000).apply(datetime.fromtimestamp)
    df_realtime["service_id"] = df_realtime["dataHora"].dt.weekday().map(
        {0: "U", 1: "U", 2: "U", 3: "U", 4: "U", 5: "S", 6: "D"})

    # 3. Excluir veículos mais antigos que 20s
    # df_realtime = df_realtime[df_realtime["direction_id"] != 0]
    df_realtime = df_realtime[df_realtime["dataHora"] > (datetime.now() - timedelta(seconds=20))]

    return df_realtime


def _haversine_np(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points
    on the earth (specified in decimal degrees)

    All args must be of equal length.

    """
    lon1, lat1, lon2, lat2 = map(np.radians, [lon1, lat1, lon2, lat2])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = np.sin(dlat/2.0)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2.0)**2

    c = 2 * np.arcsin(np.sqrt(a))
    km = 6367 * c
    return km

# TODO: add trips and shapes_with_stops
def get_current_stop(positions, trips, shapes):

    """
    1. Identifica trip_id
    2. Identifica ponto origem, ponto destino (em relação ao veículo)
    """

    # Identifica trip_id

    cols = ["direction_id", "service_id", "trip_short_name"]

    positions = positions.join(
        trips[cols + ["trip_id"]],
        on=["direction_id", "service_id", "trip_short_name"],
        how="left"
    )

    # Mapeia posições no shape e obtem stop_id_origin, stop_id_destiny
    positions = positions.join(
        shapes,
        on=["trip_id"],
        how="left"
    )

    positions["distance"] = _haversine_np(
        positions["latitude"],
        positions["longitude"],
        positions["shape_pt_lon"],
        positions["shape_pt_lat"],
        unit='m'
    )

    cols = ["codigo", "latitude", "longitude"]
    ids = positions.groupby(cols)["distance"].idxmin()

    return positions.loc[ids]

def get_prediction(origem, destino, dia_da_semana, hora_atual, next_shape_point, next_stop):
    """ Calculates de residual distance and returns prediction of current section using the model """

    # filtro em predictormodel
    modelo_mediana = MedianModel.objects.filter()
    modelo_mediana = pd.DataFrame(list(modelo_mediana.values()))

    prediction = modelo_mediana[
            (modelo_mediana.stop_id_origem == origem) &
            (modelo_mediana.stop_id_destino == destino) &
            (modelo_mediana.dia_da_semana == dia_da_semana) &
            (modelo_mediana.hora == hora_atual)
        ]["delta_tempo_minuto"].iloc[0]

    # Aqui descartando a distancia entre a posição atual e o próximo ponto do shape
    # residuo_prox_shape = (shape_posterior.shape_dist_traveled - shape_anterior.shape_dist_traveled) * (1-proj_entre_shapes)
    next_stop_distance=next_stop["shape_dist_traveled"]
    residual_distance= (next_shape_point["shape_dist_traveled"] - next_stop_distance) / next_stop_distance

    if  residual_distance > 0:
        return timedelta(minutes=prediction)*residual_distance
    else:
        return timedelta(minutes=prediction)
