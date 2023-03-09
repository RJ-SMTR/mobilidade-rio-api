from mobilidade_rio.utils.utils import stoptimes_child_or_parent
import requests
from geopy import Point
from pyproj import Transformer
import json
from datetime import datetime, timedelta
from shapely import LineString, Point
from shapely.ops import snap, split, transform
from django.utils import timezone
import pandas as pd

class Predictor():
    """
    Get prediction of vehicles (trips) using average speed
    """

    def __init__(self,
        # init 1
        stop_code: list=None, trip_short_name: list=None, direction_id: list=None,
        # init 2
        local_attributes: bool=False
        ):

        self.map_weekday_servie_id = {0: "U", 1: "U", 2: "U", 3: "U", 4: "U", 5: "S", 6: "D"}
        self._get_df_realtime()

        # init 1 - insert at least stop_code
        if stop_code and trip_short_name and direction_id:
            self.stop_code = stop_code
            self.trip_short_name = trip_short_name
            self.direction_id = direction_id

        # init 2 - no 3 params
        else:
            self._get_args_from_realtime(local_attributes)  # for testing

        # set useful parameters
        # TODO: definir qual o service_id do momento da chamada (BACKLOG)
        self._get_service_id()
        self._get_shape_id() # OK: trocar p acesso via modelo do django
        self._get_stop_info() # OK: trocar p acesso via modelo do django
        # default CRS transformer
        self.crs = Transformer.from_crs("epsg:4326", "epsg:31983")


    def _get_df_realtime(self, ignore_old_data=True) -> bool:
        # Fetch realtime api
        url = os.environ.get('API_REALTIME')
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

        # Rename cols
        df_realtime.rename(columns={"linha": "trip_short_name"}, inplace=True)
        df_realtime["direction_id"] = df_realtime["sentido"].apply(lambda x: 1 if x == 'volta' else 0)

        # Col trip_headsign
        trip_short_name = list(df_realtime['trip_short_name'].unique())
        trips = Trips.objects.filter(trip_short_name__in=trip_short_name
            ).distinct("trip_short_name","direction_id")
        df_map = pd.DataFrame(trips.values("trip_short_name","direction_id","trip_headsign"))
        df_realtime = pd.merge(df_realtime, df_map, on=["trip_short_name","direction_id"], how='left')

        # Convert unixtime -> datetime
        df_realtime["dataHora"] = (df_realtime["dataHora"] / 1000).apply(datetime.fromtimestamp)
        # Weekend
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


    def _get_args_from_realtime(self, use_local_attributes=False):
        # trip_short_name, direction_id
        if self.df_realtime.empty or use_local_attributes:
            if self.df_realtime.empty:
                print("WARNING: API realtime got no results, using local sample data")
            if use_local_attributes:
                print("INFO: Using local sample data, defined manually.")
            self.trip_short_name=["22"]
            self.direction_id=[1]
        else:
            df = self.df_realtime
            trips = Trips.objects.filter(trip_short_name__in=list(
                df['trip_short_name'].unique())).distinct("trip_short_name")
            trips = queryset_to_list(trips, "trip_short_name")
            df_valid = df.loc[df["trip_short_name"].isin(trips)].copy()
            self.trip_short_name = list(df_valid["trip_short_name"].iloc[:1])
            self.direction_id = list(df_valid['direction_id'].iloc[:1])

        # stop_code
        stoptimes = StopTimes.objects.filter(trip_id__trip_short_name__in=self.trip_short_name
            ).exclude(stop_id__parent_station__stop_code=None)[:1]
        if not stoptimes.exists():
            print("ERROR: stoptimes query is empty - trip_short_name =",self.trip_short_name)
            return
        else:
            self.stop_code = str(stoptimes[0].stop_id.parent_station.stop_code)


    def _get_service_id(self):
        # 1. Filter calendar_dates vs calendar (exception vs rule)
        today_date = timezone.now().date()
        services = CalendarDates.objects.filter(date=today_date)
        if not services.exists():
            services = Calendar.objects.filter(start_date__lte=today_date, end_date__gte=today_date)
        # 2. Filter weekday
        weekday = today_date.strftime(f"%A").lower()
        services = services.filter(**{weekday: 1})
        if not services.exists():
            print("[_get_service_id error] calendar and calendar_dates got no results - "
            f"weekday now: {weekday}")
            return
        self.service_id = services[0].service_id


    def _get_shape_id(self):
        trips = Trips.objects.filter(
            trip_short_name__in=self.trip_short_name,
            direction_id__in=self.direction_id,
            service_id=self.service_id,
        )

        # get the first trip matched, could be more - TODO: add rule to FE get the same trip_id (BACKLOG)
        # shape_id = queryset_to_list(trips, ['shape_id'])
        if trips.exists():
            self.shape_id = trips[0].shape_id
        else:
            print(
                "[get_shape_id error] trips query is empty - "
                f"trip_short_name: {self.trip_short_name} "
                f"direction_id: {self.direction_id} "
                f"service_id: {self.service_id}.",
                "Result: Query for Shapes won't be created without this query"
            )
            self.shape_id = None

  
    def _get_stop_info(self):
        """
        Get stop_id, stop_pt_lat, stop_pt_lon

        Requires:
        - `self.stop_code`
        """
        # Filter stop_code cild x parent
        stops_list = queryset_to_list(Stops.objects.filter(stop_code__in=self.stop_code))
        stoptimes = stoptimes_child_or_parent(StopTimes.objects.all(), stops_list
          ).filter(trip_id__trip_short_name__in=self.trip_short_name, 
          trip_id__direction_id__in=self.direction_id).distinct('stop_id')

        if stoptimes.exists():
            self.stop_id = stoptimes[0].stop_id.stop_id
            self.stop_pt = Point(stoptimes[0].stop_id.stop_lat, stoptimes[0].stop_id.stop_lon)
        else:
            print(f"[_get_stop_info error] stoptimes query is empty - stop_code={self.stop_code}",
                "It's necessary to create stop_id and stop_pt")


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
        "Run prediction to get eta"
        # Requirements
        if not self.trip_short_name:
            print(f"[get_eta error]: invalid trip_short_name: '{self.trip_shor_name}'")
            return
        if not self.shape_id:
            print(f"[get_eta error]: invalid shape_id: '{self.shape_id}'")
            return

        # shape position
        shape = Shapes.objects.filter(shape_id=self.shape_id)
        if not shape.exists():
            print(f"[get_eta error]: shape='{self.shape_id}' does not exists in database")
            return
        # TODO: solve error - invalid value encountered in line_locate_point
        self.shape = LineString([(s.shape_pt_lat, s.shape_pt_lon) for s in shape])#.wkt

        # Get vehicle positions from realtime API
        positions = self.df_realtime.copy()
        positions = positions[(
            positions.trip_short_name == self.trip_short_name[0]) 
            & (positions.direction_id == self.direction_id[0])
        ].copy()

        if positions.empty:
            print("ERROR: "
                f"trip_short_name={self.trip_short_name[0]} and direction_id={self.direction_id[0]} "
                "not found in API realtime (positions)"
                )
            return

        # TODO: puxar colunas q serao usadas no FE

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
        self.stop_pt_proj = self.shape.interpolate(self.shape.project(self.stop_pt))
        self.d_start_to_stop = self.get_shape_lenght(self.split_shape(self.stop_pt_proj))

        positions["d_start_to_stop"] = self.d_start_to_stop
        positions["d_px_to_stop"] = self.d_start_to_stop - positions.d_start_to_px
        positions["estimated_time_arrival"] = positions.apply(lambda x: 60 * x.d_px_to_stop / float(
            x.velocidade) if float(x.velocidade) > 0 else x.d_px_to_stop, axis=1)

        positions = positions[positions.estimated_time_arrival >= 0]
        positions = positions.sort_values("estimated_time_arrival")

        return positions[[
                # API fields
                "codigo",                   # pk
                "dataHora",                 # created at
                "latitude",                 # current vehicle lat
                "longitude",                # current vehicle lon
                "trajeto",                  # API name of trip
                    # trajeto: 22 - J. OCEÂNICO X ALVORADA (PARADOR) [VOLTA]
                    # trajeto: <trip_short_name> - <API.route_long_name> [<sentido.uppercase()>]
                "velocidade",               # current vehicle speed

                # GTFS fields
                "direction_id",             # sentido = ida,volta vs direction_id = 0,1
                "trip_headsign",
                "trip_short_name",          # linha

                # Frontend fields
                "estimated_time_arrival",    # in minutes?
        ]].to_dict(orient="records")


    def __repr__(self) -> str:
        "Debug attributes"
        return f"""\
Predictor values:
    input (1-n):
        stop_code: {self.stop_code}
        trip_short_name: {self.trip_short_name}
        direction_id: {self.direction_id}
    processing (1):
        service_id: '{self.service_id}'
        shape_id: {self.shape_id}\
        """
