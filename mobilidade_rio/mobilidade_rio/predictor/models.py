from django.db import models

# Create your models here.
class ShapeWithStops(models.Model):
    # from trips
    trip_short_name = models.CharField(max_length=500, blank=True, null=True) # route_short_name
    
    # from stop_times
    trip_id = models.CharField(max_length=500, blank=True)
    stop_sequence = models.CharField(max_length=500, blank=True, null=True)
    stop_id = models.CharField(max_length=500, blank=True)
    shape_dist_traveled = models.CharField(max_length=500, blank=True, null=True)

    # from shapes
    shape_id = models.CharField(max_length=500, blank=True)
    shape_pt_sequence = models.CharField(max_length=500, blank=True, null=True)
    shape_pt_lat = models.CharField(max_length=500, blank=True, null=True)
    shape_pt_lon = models.CharField(max_length=500, blank=True, null=True)
    



class Predictor:

    """
    
    self.df_real_time : pd.DataFrame com dados real time do gtfs
    self.trip_stops : pd.DataFrame com todas as paradas de todas as linhas
    self.trip_ids : pd.DataFrame com a relação das linhas e suas trip_ids
    self.bus_states : dict para guardar informacoes dos onibus, como seu tripid real

    """


    def __init__(self):
        self.bus_states = {}
        self.capture_trip_stops()
        self.get_model()
        
    def capture_real_time_data(self,trip_short_name_list):
        """ Captura os dados em tempo real da API do GTFS """
        x=requests.get("http://brj.citgis.com.br:9977/gtfs-realtime-exporter/findAll/json")
        real_time = pd.read_json(x.text)
        #print(real_time.columns)
        real_time["comunicacao"] = real_time["comunicacao"].apply(datetime.fromtimestamp)
        real_time["inicio_viagem"] = real_time["inicio_viagem"].apply(datetime.fromtimestamp) 
        self.df_real_time = real_time.loc[real_time["linha"].isin(trip_short_name_list)]
        #self.df_real_time = real_time


    def capture_trip_stops(self):
        """ Recovers preprocessed data with 'shape' and 'stops' info joined """

        stops_path = os.path.join(current_dir, 'Dados/gtfs_brt_treated/shapes_with_stops.csv')
        self.trip_stops = pd.read_csv(stops_path)
        self.trip_ids = self.trip_stops[["trip_id", "route_short_name"]].dropna().drop_duplicates()
        self.trip_ids["direction"] = [trip_id[TRIP_ID_INDICE_SENTIDO-1] for trip_id in self.trip_ids["trip_id"]]
        #trocar por retorno de ShapesWithStops.



    def get_true_tripid(self, bus_id, service_line, communication, trip_start, cur_latitude, cur_longitude):
        """ Returns true tripid by actual bus starting location communication.

            Output: tripid if we have information about the begining of trip.
                    None if we dont have information saved.
        """

        diferenca_tempo = (communication - trip_start).total_seconds()
        tripid = None

        # Temos um start location definido no cache
        if bus_id in self.bus_states and self.bus_states[bus_id]["trip_start"] != trip_start:
            tripid = self.bus_states[bus_id]["tripid"]
        #    print(f"Using saved trip_id {tripid} for {bus_id}")

        # Estamos no inicio de uma corrida
        elif diferenca_tempo <= 30:
            coords_real_time = (cur_latitude, cur_longitude)

            # Obtem a stop inicial para cada uma das trips relacionadas a essa rota
            starts_trips = self.trip_stops[
                (self.trip_stops.route_short_name == service_line) & 
                (self.trip_stops.stop_sequence == 1)
            ]

            if len(starts_trips) == 0:
                return tripid

            # Descobre qual inicio de trip esta mais perto do ponto atual real time
            distances = starts_trips.apply(lambda row: haversine(coords_real_time, (row["latitude"], row["longitude"])), axis=1)
            min_distance_idx = distances.idxmin()
            tripid = starts_trips.loc[min_distance_idx]["trip_id"]
            
            # Cacheia a informacao de trip
            if bus_id not in self.bus_states:
                self.bus_states[bus_id] = {}
            self.bus_states[bus_id]["tripid"] = tripid
            self.bus_states[bus_id]["trip_start"] = trip_start

            #print(f"Set {bus_id} to {tripid}")
            
        return tripid


    def get_trip_id(self, bus_id, service_line, communication, trip_start, cur_latitude, cur_longitude, declared_direction):
        """ Given information about current bus, return the true trip_id or the declared one.
            
            Output: Current TripId - can be from the gtfs data itself or from the processed start location of trip.
        """
        
        true_tripid = self.get_true_tripid(bus_id, service_line, communication, trip_start, cur_latitude, cur_longitude)

        if true_tripid is not None:
            return true_tripid
        
        else:
            line_trip_ids = self.trip_ids[
                (self.trip_ids["route_short_name"] == service_line) &
                (self.trip_ids["direction"] == declared_direction)
            ]["trip_id"]

            if len(line_trip_ids) == 0:
                return None

            return line_trip_ids.iloc[0]
    

    def get_residual_distance(self, df, current_index, proj_entre_shapes):
        """ Returns the proportion of distance between current location and next stop.

            Represented by the ===>: 
                [STOP1] ----> X -----[BUS]=====> X ======> X ======> [STOP2]

            The Xs represent shapes marks (not real stops)
        """

        # 1. calculamos a distancia da posicao atual ate o proximo shape
        # Apenas a parte: [BUS]=====> X
        shape_anterior = df.loc[current_index]
        shape_posterior = df.loc[current_index+1]
        residuo_prox_shape = (shape_posterior.shape_dist_traveled - shape_anterior.shape_dist_traveled) * (1-proj_entre_shapes)

        # 2. calculamos a distancia do proximo shape para o proximo stop
        # Apenas a parte: X ======> X ======> [STOP2]
        stop_id_posterior = shape_anterior.next_stop_id
        shape_dist_stop_id_posterior = df[df.stop_id == stop_id_posterior].iloc[0].shape_dist_traveled
        shape_dist_shape_posterior = shape_posterior.shape_dist_traveled
        residuo_ate_stop_posterior = shape_dist_stop_id_posterior - shape_dist_shape_posterior

        # 3. calculamos a total no intervalo entre stops
        # Tudo: [STOP1] ---> [STOP2]
        stop_id_anterior = shape_anterior.previous_stop_id
        shape_dist_stop_id_anterior = df[df.stop_id == stop_id_anterior].iloc[0].shape_dist_traveled
        distancia_total_trecho = shape_dist_stop_id_posterior - shape_dist_stop_id_anterior

        return (residuo_prox_shape + residuo_ate_stop_posterior) / distancia_total_trecho


    def get_next_stops(self, latitude_atual, longitude_atual, shapes_stops_trip):
        """ Given the current latitude and longitude, and the stops for the trip, returns the next stops. """
        
        shapes_stops_trip = shapes_stops_trip.sort_values("shape_dist_traveled")
        
        ponto_atual = [latitude_atual, longitude_atual]
        
        # Verifica se esta no raio do terminal de origem
        coord_terminal = (shapes_stops_trip.iloc[0]["latitude"], shapes_stops_trip.iloc[0]["longitude"])
        coord_atual = (latitude_atual, longitude_atual)
        distancia_terminal = haversine(coord_terminal, coord_atual, unit='m')
        if distancia_terminal < 100:
            return shapes_stops_trip.dropna(subset=["stop_id"]), 0, shapes_stops_trip.iloc[0].previous_stop_id
        
        # Verifica se esta no raio do terminal de destino
        coord_terminal = (shapes_stops_trip.iloc[-1]["latitude"], shapes_stops_trip.iloc[-1]["longitude"])
        coord_atual = (latitude_atual, longitude_atual)
        distancia_terminal = haversine(coord_terminal, coord_atual, unit='m')
        if distancia_terminal < 100:
            # return shapes_stops_trip.dropna(subset=["stop_id"]).iloc[-1:]
            return pd.DataFrame(columns=shapes_stops_trip.columns), 0, shapes_stops_trip.iloc[-1].previous_stop_id

        # Calcula nos casos em que o onibus esta em transito nos demais pontos
        df = shapes_stops_trip
        pontos_antes = df[["latitude", "longitude"]].iloc[:-1].values
        pontos_depois = df[["latitude", "longitude"]].iloc[1:].values

        v1 = pontos_depois - pontos_antes
        v2 = ponto_atual - pontos_antes
        v1_norm = linalg.norm(v1, axis=1) 

        # Atraves da projecao do ponto atual em cada um dos segmentos de trecho
        # checo se o ponto atual esta projetado neste segmento.
        proj = np.sum(v1 * v2, axis=1)/(v1_norm**2)
        filtro_proj = (0 <= proj) & (proj <= 1)
        if not filtro_proj.any():
            return pd.DataFrame(columns=shapes_stops_trip.columns), 0, None

        # Obtenho pra cada trecho que passou na projecao, a distancia do ponto atual
        # ate o segmento de reta. Caso mais de um segmento tenha a projecao do ponto
        # obtemos o de menor distancia.
        vproj = v1 * proj.reshape([-1,1])
        distancia_reta = linalg.norm(v2-vproj, axis=1)
        if len(distancia_reta[filtro_proj]) == 0:
            print(distancia_reta, filtro_proj)
        best_idx_in_filter = distancia_reta[filtro_proj].argmin()
        best_idx = df.iloc[:-1][filtro_proj].index[best_idx_in_filter]

        # Obtencao da distancia residual do ponto atual ate a proxima stop
        proj_entre_shapes = proj[filtro_proj][best_idx_in_filter]
        residual_distance = self.get_residual_distance(df, best_idx, proj_entre_shapes)

        # Retorna todos os stop_ids a partir do trecho em que foi identificado o atual
        next_stops = df.loc[best_idx:].iloc[1:].dropna(subset=["stop_id"])
        return next_stops, residual_distance, df.loc[best_idx].previous_stop_id
    

    def get_prediction(self, origem, destino, dia_da_semana, hora_atual):
        """ Returns prediction of current section using the model """

        prediction = self.model[ 
                (self.model.stop_id_origem == origem) & 
                (self.model.stop_id_destino == destino) &
                (self.model.dia_da_semana == dia_da_semana) & 
                (self.model.hora == hora_atual) 
            ]["delta_tempo_minuto"].iloc[0]
        
        return timedelta(minutes=prediction)


    def predict_individual_arrivals(self, real_time_row):
        """ Given a row of df_real_time table, predict arrivals for each stop in sequence.
        
            Composed by the predictions between next stops and the residual prediction from
            curent location to the first next stop.
        """

        bus_id = real_time_row["vei_nro_gestor"]
        latitude = real_time_row["latitude"]
        longitude = real_time_row["longitude"]
        linha = real_time_row["linha"]
        nome_itinerario = real_time_row["nomeItinerario"]
        inicio_viagem = real_time_row["inicio_viagem"]
        comunicacao = real_time_row["comunicacao"]
        dia_da_semana = comunicacao.weekday()
        hora_atual = comunicacao.hour

        sentido_declarado = map_direction(nome_itinerario)

        trip_id = self.get_trip_id(bus_id, linha, comunicacao, inicio_viagem, latitude, longitude, sentido_declarado)
        if trip_id is None: 
            #print(f"Null tripid returned for {linha}.")
            return None

        # try:
        trip_stops = self.trip_stops[self.trip_stops.trip_id == trip_id]
        next_stops, residual_distance, previous_stop_id = self.get_next_stops(latitude, longitude, trip_stops)
        # except:
        #     print(f"Não foi possível encontrar stops para {trip_id}")
        #     return pd.DataFrame()

        if len(next_stops) == 0:
            return pd.DataFrame()

        # Tempo Residual no Trecho Atual
        if residual_distance > 0:
            stop_anterior = previous_stop_id
            stop_posterior = next_stops.iloc[0].stop_id

            pred = self.get_prediction(stop_anterior, stop_posterior, dia_da_semana, hora_atual)
            tempo_residual = pred*residual_distance
        else:
            tempo_residual = timedelta(minutes=0)

        # Predicoes de cada trecho
        if len(next_stops) > 1:
            predicoes = next_stops.iloc[:-1].apply(
                lambda row: self.get_prediction(row.stop_id, row.next_stop_id, dia_da_semana, hora_atual),
                axis=1
            ).tolist()
            predicoes.insert(0,0)
        else:
            predicoes = [0]

        # Predicao final para cada stop seguinte
        predicoes_horario = pd.to_timedelta(pd.Series(predicoes)).cumsum() + comunicacao + tempo_residual
        
        predicao_final = pd.DataFrame({
            'trip_id': trip_id,
            'chegada': predicoes_horario.values,
            'stop_name': next_stops.stop_name.values,
            'stop_id': next_stops.stop_id.values,
            'latitude': next_stops.latitude.values,
            'longitude': next_stops.longitude.values,
            'bus_id': bus_id,
            'communication': comunicacao,
            'first_communication': inicio_viagem
        })

        return predicao_final
    

    def get_model(self):
        # TODO: uso apenas momentaneo, vai ser uma api separada
        stops_path = os.path.join(current_dir, f'Modelos/Mediana/geral.parquet')
        modelo = pd.read_parquet(stops_path, engine='fastparquet')
        self.model = modelo


    def predict_all_arrivals(self):
        lista_predicoes = self.df_real_time.apply(self.predict_individual_arrivals, axis=1).values
        predicoes = pd.concat(lista_predicoes, ignore_index=True)
        
        return predicoes