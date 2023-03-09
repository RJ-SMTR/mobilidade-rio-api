"""Utils for predictor app"""
import os
import json
from datetime import datetime, timedelta
from pyproj import Transformer
import requests
from shapely import LineString, Point
from shapely.ops import snap, split, transform
from django.utils import timezone
import pandas as pd
from mobilidade_rio.pontos.models import *

class Predictor():
    """
    Input:
        stop_code           1st option, easy for frontend to implement
        direction_id        2nd option, frontend will need more steps to find it
        trip_short_name     3rd option, user in app will need to select platform in UI
        debug_cols          show extra cols in output, for debugging purposes

    Output:
        Dataframe with realtime API fields + ETA (Estimated Time of Arrival)
    """
    def __init__(self,
        stop_code:list=None, direction_id:list=None, trip_short_name:list=None,
        debug_cols:bool=False
        ):

        self.map_weekday_servie_id = {0: "U", 1: "U", 2: "U", 3: "U", 4: "U", 5: "S", 6: "D"}
        self.map_stops = pd.DataFrame()
        self.df_realtime = pd.DataFrame()

        self._get_df_realtime()

        # init 1 - insert at least stop_code
        self.stop_code = stop_code
        self.trip_short_name = trip_short_name
        self.direction_id = direction_id
        self.debug_cols = debug_cols

        # init 2 - no 3 params, add if not exists
        self._get_inputs()

        # set useful parameters
        # TODO: definir qual o service_id do momento da chamada (BACKLOG)
        self._get_service_id()
        self._get_shape_id() # OK: trocar p acesso via modelo do django
        # default CRS transformer
        self.crs = Transformer.from_crs("epsg:4326", "epsg:31983")


    def _get_df_realtime(self, ignore_old_data=True) -> bool:
        # Fetch realtime api
        # TODO: can be good to set as env only
        url = os.environ.get('API_REALTIME', "https://dados.mobilidade.rio/gps/brt")
        print("URL ENV:", url)
        if not url:
            print("[_get_df_realtime error]: Envs not found")
            return False
        # headers = json.loads(headers)
        api_response = requests.get(url,timeout=10)
        json_api_response = json.loads(api_response.text)
        if api_response.status_code != 200:
            print("[_get_df_realtime error]: Request to API realtime got error:")
            print(json_api_response)
            return

        df_realtime = pd.DataFrame(pd.json_normalize(json_api_response['veiculos']))

        # TODO: mudar nomes das colunas q forem do gtfs (linha -> trip_short_name, ...)
        df_realtime.rename(columns={"linha": "trip_short_name"}, inplace=True)
        df_realtime["direction_id"] = df_realtime["sentido"].apply(lambda x: 1 if x == 'volta' else 0)

        # trip_headsign
        trip_short_name = list(df_realtime['trip_short_name'].unique())
        trips = Trips.objects.filter(trip_short_name__in=trip_short_name
            ).distinct("trip_short_name","direction_id")
        df_map = pd.DataFrame(trips.values("trip_short_name","direction_id","trip_headsign"))
        df_realtime = pd.merge(df_realtime, df_map, on=["trip_short_name","direction_id"], how='left')


        # OK: converter unixtime -> datetime
        df_realtime["dataHora"] = (df_realtime["dataHora"] / 1000).apply(datetime.fromtimestamp)
        # weekday
        # TODO @yxuo: Confirmar se o map {5:"S",6:"D"} está correto.
        df_realtime["service_id"] = df_realtime["dataHora"].dt.weekday.map(self.map_weekday_servie_id)

        # Ignore vehicles older than 20s
        if ignore_old_data:
            df_realtime = df_realtime[df_realtime["dataHora"]
                                    > (datetime.now() - timedelta(seconds=20))]
            if df_realtime.empty:
                print("[_get_df_realtime error] no vehicles in the last 20s.")
                return False

        self.df_realtime = df_realtime
        return True


    def _get_inputs(self):
        if self.df_realtime.empty:
            if self.df_realtime.empty:
                print("[_get_inputs error]: API realtime got no results")
                return

        # Get valid trips (api vs database)
        df_api = self.df_realtime.copy()
        df_api = df_api.drop_duplicates(subset=["trip_short_name","direction_id"])
        unique_trips = Trips.objects.all().distinct("trip_short_name", "direction_id")
        df_trips = pd.DataFrame(unique_trips.values("trip_short_name", "direction_id","trip_id"))
        # Create A
        df_valid = pd.merge(df_api, df_trips, on=["trip_short_name","direction_id"], how='left')
        # Create B
        children = StopTimes.objects.all().exclude(  # valid_stoptimes_child
            stop_id__parent_station__stop_code=None)
        if not children.exists():
            print("ERROR: stoptimes has no stop child - stoptimes total len:",len(children))
            return

        # Filter trips with inputs - 1,2,3 filter A
        # TODO: filter combination of {trip_short_name: [direction_id]}
        if self.trip_short_name:
            df_valid = df_valid[df_valid["trip_short_name"].isin(self.trip_short_name)]
        if self.direction_id:
            df_valid = df_valid[df_valid["direction_id"].isin(self.direction_id)]
        if self.stop_code:
            # filter children by stop_code and get trips
            list_children_trips = list(children.filter(
                stop_id__parent_station__stop_code__in=self.stop_code).distinct("trip_id"
                ).values_list("trip_id", flat=True))
            df_valid = df_valid[df_valid["trip_id"].isin(list_children_trips)]
            
        # Set inputs - A updates 1,2
        if not self.trip_short_name:
            self.trip_short_name = list(df_valid["trip_short_name"].unique())
        if not self.direction_id:
            self.direction_id = list(df_valid['direction_id'].unique())

        # A (1,2,3) updates B
        children = children.filter(
            trip_id__trip_short_name__in=df_valid["trip_short_name"].to_list(),
            trip_id__direction_id__in=df_valid["direction_id"].to_list(),
            )
        if not self.stop_code:
            # B updates 3
            self.stop_code = list(children.distinct("stop_id__parent_station__stop_code"
                ).values_list("stop_id__parent_station__stop_code",flat=True))

        # Get map of stops
        map_stops = pd.DataFrame(children.values(
            "stop_id",  # debug
            "trip_id",  # debug
            "stop_id__parent_station__stop_code",
            "trip_id__trip_short_name",
            "trip_id__direction_id",
            "trip_id__shape_id",
            ))
        map_stops.columns = map_stops.columns.str.replace(r'^.*__', '', regex=True)
        self.map_stops = map_stops


    def _get_service_id(self):
        # 1. Filtrar data do calendar_dates vs calendar (excessão vs regra)
        today_date = timezone.now().date()
        services = CalendarDates.objects.filter(date=today_date)
        if not services.exists():
            services = Calendar.objects.filter(start_date__lte=today_date, end_date__gte=today_date)
        # 2. Filtrar dia da semana
        weekday = today_date.strftime(f"%A").lower()
        services = services.filter(**{weekday: 1})
        if not services.exists():
            print("[_get_service_id error] calendar and calendar_dates got no results - "
            f"weekday now: {weekday}")
            return
        self.service_id = list(services.values_list("service_id", flat=True))


    # move to _get_input
    def _get_shape_id(self):
        # get the first trip matched, could be more - TODO: add rule to FE get the same trip_id (BACKLOG)
        # shape_id = queryset_to_list(trips, ['shape_id'])

        trips = Trips.objects.filter(
            trip_short_name__in=self.trip_short_name,
            direction_id__in=self.direction_id,
            service_id__in=self.service_id,
        )
        if not trips.exists():
            print(
                "[get_shape_id error] trips query is empty - "
                f"trip_short_name: {self.trip_short_name} "
                f"direction_id: {self.direction_id} "
                f"service_id: {self.service_id}.",
                "Result: Query for Shapes won't be created without this query"
            )
            self.shape_id = None
            return

        self.shape_id = list(trips.distinct("shape_id").values_list("shape_id", flat=True))


    def split_shape(self, pt, part=0):
        """
        Splits a shape based on a point. By default gets only the first part.
        """
        # print(split(snap(self.shape, pt, 1e-8), pt).geoms[part])
        return split(snap(self.shape, pt, 1e-8), pt).geoms[part]


    def get_shape_lenght(self, shape, unit="km"):
        """
        Calculates the shape lenght over the choosen CRS. To change the CRS, check the attribute self.crs.
        """
        # print([s for s in shape if not s])
        lenght = transform(self.crs.transform, shape).length
        if unit == "km":
            return lenght / 1000
        return lenght


    def get_eta(self):
        # Requirements
        if not self.trip_short_name:
            print(f"[get_eta error]: invalid trip_short_name: '{self.trip_short_name}'")
            return None
        if not self.shape_id:
            print(f"[get_eta error]: invalid shape_id: '{self.shape_id}'")
            return None
        
        # If filter inputs got no results
        if self.map_stops.empty:
            return None

        # Concat results for each shape (trip_short_name)
        rt = self.df_realtime
        ret = pd.DataFrame(columns=rt.columns)
        for shape_id in self.shape_id:

            # shape position
            shape = Shapes.objects.filter(shape_id=shape_id)
            df = self.map_stops.copy()
            # ? Each map_stops is a stoptime row with extra fields, so normally direction_id has 1 value
            # ? You can filter stoptimes by shape_id, trip_short_name, direction_id
            #   to check result
            df_shape = df.loc[df["shape_id"]==shape_id]
            trip_short_name = list(df_shape["trip_short_name"].unique())
            direction_id = list(df_shape["direction_id"].unique())

            # stop pt per stop_code (parent) to simplify
            # TODO: to increase precision, for each shape filter by stop child pos
            # ? For now it only filter bt 1 stop_code
            stops = Stops.objects.filter(stop_code=self.stop_code[0])
            stop_pt = Point(stops[0].stop_lat, stops[0].stop_lon)

            # TODO: solve error - invalid value encountered in line_locate_point
            self.shape = LineString([(s.shape_pt_lat, s.shape_pt_lon) for s in shape])#.wkt

            # Get vehicle positions in this shape
            positions = rt.copy()
            # TODO: filter combination of {trip_short_name: [direction_id]}
            positions = positions[(
                positions.trip_short_name.isin(trip_short_name)) 
                & (positions.direction_id.isin(direction_id))
            ].copy()

            if positions.empty:
                print("[get_eta warning]: "
                    f"trip_short_name={trip_short_name} and direction_id={direction_id} "
                    "not found in API realtime (positions)",
                    f"realtime results: {len(rt.loc[rt['trip_short_name'].isin(trip_short_name)])}"
                    )
                continue

            # get vehicle positions and project them into the shape
            positions["px"] = positions.apply(lambda x: Point(x.latitude, x.longitude), axis=1)
            # TODO: solve error - invalid value encountered in line_locate_point (interpolate?, projecet?)
            positions["px_proj"] = positions.apply(lambda x: self.shape.interpolate(self.shape.project(x.px)), axis=1)

            # calculate distance from shape_start_pt to vehicle
            positions["d_shape"] = positions.px_proj.apply(lambda x: self.get_shape_lenght(self.shape))
            positions["d_start_to_px"] = positions.px_proj.apply(
                lambda x: self.get_shape_lenght(self.split_shape(x)))

            # calculate distance from vehicle to stop
            # TODO: solve error - invalid value encountered in line_locate_point (interpolate?, projecet?)
            stop_pt_proj = self.shape.interpolate(self.shape.project(stop_pt))
            d_start_to_stop = self.get_shape_lenght(self.split_shape(stop_pt_proj))

            positions["d_start_to_stop"] = d_start_to_stop
            positions["d_px_to_stop"] = d_start_to_stop - positions.d_start_to_px
            positions["estimated_time_arrival"] = positions.apply(lambda x: 60 * x.d_px_to_stop / float(
                x.velocidade) if float(x.velocidade) > 0 else x.d_px_to_stop, axis=1)

            positions = positions[positions.estimated_time_arrival >= 0]
            positions = positions.sort_values("estimated_time_arrival")
            positions["shape_id"] = shape_id
            positions["stop_code"] = self.stop_code[0]
            positions["shape_id"] = shape_id

            if ret.empty:
                ret = positions.copy()
            else:
                ret = pd.concat([ret, positions]).copy()
        print("len ret FINAL:", len(ret))

        # TODO: mudar nomes das colunas q forem do gtfs (linha -> trip_short_name, ...)
        ret_cols = [
            # API fields
            "codigo",                   # pk
            "dataHora",                 # created at
            "latitude",                 # current vehicle lat
            "longitude",                # current vehicle lon
            # trajeto: 22 - J. OCEÂNICO X ALVORADA (PARADOR) [VOLTA]
            # trajeto: <trip_short_name> - <API.route_long_name> [<sentido.uppercase()>]
            "trajeto",                  # API name of trip
            "velocidade",
            
            # GTFS fields
            "trip_short_name",          # linha
            "direction_id",             # sentido = ida,volta vs direction_id = 0,1
            "trip_headsign",

            # Frontend fields
            "estimated_time_arrival",   # in minutes?
        ]
        if self.debug_cols:
            ret_cols += [
                # Debug fields
                "shape_id",                 # classified by shape_id
                "stop_code",                # It uses the first stop_code
            ]
        return ret[ret_cols].to_dict(orient="records")


    def __repr__(self) -> str:
        str_map_stops = "Empty"
        if not self.map_stops.empty:
            str_map_stops = f"""
            unique stop_code: {len(self.map_stops["stop_code"].unique())}
            unique trip_short_name: ({len(self.map_stops["trip_short_name"].unique())})
            unique direction_id: {len(self.map_stops["direction_id"].unique())}
            unique shape_id: {len(self.map_stops["shape_id"].unique())}
            """

        return f"""\
Predictor values:
    input:
        stop_code: ({len(self.stop_code)}) {self.stop_code}
        trip_short_name: ({len(self.trip_short_name)}) {self.trip_short_name}
        direction_id: ({len(self.direction_id)}) {self.direction_id}
    processing:
        service_id: '{self.service_id}'
        shape_id: ({len(self.shape_id)}) {self.shape_id}
        map_stops: ({len(self.map_stops)}) {str_map_stops}
        df_realtime: ({len(self.df_realtime)})
        \
        """
