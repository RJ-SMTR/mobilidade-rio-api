import os
import requests
from datetime import datetime, timedelta
import pandas as pd

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

    # TODO: ainda precisa filtrar por trip_id aqui?

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
