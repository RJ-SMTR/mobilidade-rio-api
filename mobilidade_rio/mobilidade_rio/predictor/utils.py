import os
import requests
from datetime import datetime, timedelta
import pandas as pd

def get_realtime(df_real_time: pd.DataFrame, trip_short_name_list: list, has_trip: bool):
    # Get realtime data from API
    url=os.environ.get('API_REAL_TIME')
    x=requests.get(url)
    real_time = pd.read_json(x.text)

    real_time["comunicacao"] = real_time["comunicacao"].apply(datetime.fromtimestamp)
    real_time["inicio_viagem"] = real_time["inicio_viagem"].apply(datetime.fromtimestamp) 
    if has_trip:
        # Filter by trip via 'trip_short_name' in 'linha' column
        df_real_time = real_time.loc[real_time["linha"].isin(trip_short_name_list)]
    else:
        df_real_time = real_time

    # return df_real_time