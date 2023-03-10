"""Utils for predictor app"""
import os
from datetime import datetime, timedelta
from pyproj import Transformer
import requests
from shapely.geometry import LineString, Point
from shapely.ops import snap, split, transform
from django.utils import timezone
import pandas as pd
from mobilidade_rio.pontos.models import Stops, Trips, Calendar, CalendarDates, Shapes


class Predictor:  # pylint: disable=C0301
    # TODO: change to google style: https://google.github.io/styleguide/pyguide.html#38-comments-and-docstrings # pylint: disable=W0511
    """
    Input:
        stop_code           1st option, easy for frontend to implement
        direction_id        2nd option, frontend will need more steps to find it
        trip_short_name     3rd option, user in app will need to select platform in UI
        debug_cols          show extra cols in output, for debugging purposes

    Output:
        Dataframe with realtime API fields + ETA (Estimated Time of Arrival)
    """

    def __init__(
        self,
        stop_id: int,
        direction_id: list = None,
        trip_short_name: list = None,
        service_id: str = None,
    ):

        self.stop_id = stop_id
        self.trip_short_name = trip_short_name
        self.direction_id = direction_id
        self.service_id = self._get_service_id() if service_id is None else service_id
        self.stop_pt = self._get_stop_pt()

        # set inputs to run iteration
        self.inputs = self._set_inputs()

        # default CRS transformer
        self.crs = Transformer.from_crs("epsg:4326", "epsg:31983")

    def _get_stop_pt(self):
        """
        Get stop point from stop_id.
        """
        stop = Stops.objects.get(stop_id=self.stop_id)
        return Point(stop.stop_lon, stop.stop_lat)

    def _set_inputs(self):
        """
        For each direction_id and trip_short_name, get the shape_id
        and set the inuts for the model.
        """
        inputs = []
        for direction_id in self.direction_id:
            for trip_short_name in self.trip_short_name:
                shape_id = self._get_shape_id(
                    trip_short_name, direction_id, self.service_id
                )
                inputs.append(
                    {
                        "stop_id": self.stop_id,
                        "direction_id": direction_id,
                        "trip_short_name": trip_short_name,
                        "service_id": self.service_id,
                        "shape_id": shape_id,
                    }
                )

        return inputs

    def _get_realtime(self, max_delay_secs=120):

        # TODO: change to internal API, get secrets from Vault # pylint: disable=W0511
        url = os.environ.get("API_REALTIME", "https://dados.mobilidade.rio/gps/brt")
        response = requests.get(url, timeout=5)

        if not response.ok:
            raise Exception(f"API error: {response.status_code} - {response.reason}")

        data = pd.DataFrame(pd.json_normalize(response.json()["veiculos"]))

        # rename columns
        data.rename(columns={"linha": "trip_short_name"}, inplace=True)
        data["direction_id"] = data["sentido"].apply(lambda x: 1 if x == "volta" else 0)

        # conver unix to datetime
        data["dataHora"] = (data["dataHora"] / 1000).apply(datetime.fromtimestamp)

        data = data[
            data["dataHora"] > (datetime.now() - timedelta(seconds=max_delay_secs))
        ]

        if data.empty:
            raise Exception("API error: no results")

        return data

    def _get_service_id(self):

        today_date = timezone.now().date()

        # Check for date exceptions
        services = CalendarDates.objects.filter(date=today_date).filter(
            exception_type=1
        )

        if len(services) > 1:
            raise Exception(
                "Multiple services found for today. Please set a specific service_id."
            )
        if len(services) == 1:
            return services.values_list("service_id", flat=True)[0]

        # Check for regular service
        weekday = today_date.strftime("%A").lower()
        services = Calendar.objects.filter(
            start_date__lte=today_date, end_date__gte=today_date
        ).filter(**{weekday: 1})

        if len(services) > 1:
            return Exception(
                "Multiple services found for today. Please set a specific service_id."
            )
        if len(services) == 0:
            raise Exception("No service found for today.")

        return services.values_list("service_id", flat=True)[0]

    def _get_shape_id(self, trip_short_name, direction_id, service_id):
        # get the first trip matched, could be more - TODO: add rule to
        # FE get the same trip_id (BACKLOG) # pylint: disable=W0511
        # shape_id = queryset_to_list(trips, ['shape_id'])

        trips = Trips.objects.filter(
            trip_short_name__in=trip_short_name,
            direction_id__in=direction_id,
            service_id__in=service_id,
        )

        if len(trips) == 0:
            raise Exception("No trips found for the given inputs.")

        shapes = trips.distinct("shape_id")

        if len(shapes) > 1:
            raise Exception(
                "Multiple shapes found for the given inputs. Please set specfic a shape_id."
            )
        if (
            len(shapes) == 0
        ):  # works if shape_id is null? TODO: check for this chatch # pylint: disable=W0511
            raise Exception("No shapes found for the given inputs.")

        return shapes.values_list("shape_id", flat=True)[0]

    def _split_shape(self, shape, break_pt, part=0):
        """
        Splits a shape based on a point. By default gets only the first part.
        """
        return split(snap(shape, break_pt, 1e-8), break_pt).geoms[part]

    def _get_shape_lenght(self, shape, unit="km"):
        """
        Calculates the shape lenght over the choosen CRS. To change the CRS, check the attribute self.crs.
        """
        # print([s for s in shape if not s])
        lenght = transform(self.crs.transform, shape).length
        if unit == "km":
            return lenght / 1000
        return lenght

    def get_trip_eta(self, direction_id, trip_short_name, shape_id):
        """
        Gets ETA of all vehicle to a stop, operating on a specific trip.
        """

        # get vehicle positions
        positions = self._get_realtime()
        positions = positions[
            (positions.trip_short_name == trip_short_name)
            & (positions.direction_id == direction_id)
        ].copy()

        # get shape
        shape = Shapes.objects.filter(shape_id=shape_id)
        shape = LineString(list(zip(shape.shape_pt_lat, shape.shape_pt_lon)))  # .wkt

        # project vehicle positions into the shape
        positions["px"] = positions.apply(
            lambda x: Point(x.latitude, x.longitude), axis=1
        )
        positions["px_proj"] = positions.apply(
            lambda x: shape.interpolate(shape.project(x.px)), axis=1
        )

        # calculate distance from shape_start_pt to vehicle
        positions["d_shape"] = positions.px_proj.apply(
            lambda x: self._get_shape_lenght(shape)
        )
        positions["d_start_to_px"] = positions.px_proj.apply(
            lambda x: self._get_shape_lenght(self._split_shape(shape, x))
        )

        # calculate distance from shape_start_pt to stop
        stop_pt_proj = shape.interpolate(shape.project(self.stop_pt))
        positions["d_start_to_stop"] = self._get_shape_lenght(
            self._split_shape(shape, stop_pt_proj)
        )

        # calculate distance from vehicle to stop (diff from above ones)
        positions["d_px_to_stop"] = positions.d_start_to_stop - positions.d_start_to_px

        # set expected minimum speed
        positions["velocidade"] = positions["velocidade"].fillna(0).apply(
            lambda x: 30 if float(x) < 30 else float(x)
        )

        # convert to eta
        positions["estimated_time_arrival"] = positions.apply(
            lambda x: 60 * x.d_px_to_stop / x.velocidade,
            axis=1,
        )

        positions = positions[positions.estimated_time_arrival >= 0].sort_values(
            "estimated_time_arrival"
        )

        cols = [
            "codigo",  # pk
            "dataHora",  # created at
            "latitude",  # current vehicle lat
            "longitude",  # current vehicle lon
            "velocidade",
            "trip_short_name",  # linha
            "direction_id",  # 0, 1
            "estimated_time_arrival",  # in minutes
        ]

        return positions[cols].to_dict(orient="records")

    def run_eta(self):
        """
        Runs ETA of all vehicle to a single stop.
        """
        for params in self._set_inputs():
            self.get_trip_eta(**params)


# TODO: precisa manter esse __repr__? # pylint: disable=W0511
#     def __repr__(self) -> str:
#         str_map_stops = "Empty"
#         if not self.map_stops.empty:
#             str_map_stops = f"""
#             unique stop_code: {len(self.map_stops["stop_code"].unique())}
#             unique trip_short_name: ({len(self.map_stops["trip_short_name"].unique())})
#             unique direction_id: {len(self.map_stops["direction_id"].unique())}
#             unique shape_id: {len(self.map_stops["shape_id"].unique())}
#             """

#         return f"""\
# Predictor values:
#     input:
#         stop_code: ({len(self.stop_code)}) {self.stop_code}
#         trip_short_name: ({len(self.trip_short_name)}) {self.trip_short_name}
#         direction_id: ({len(self.direction_id)}) {self.direction_id}
#     processing:
#         service_id: '{self.service_id}'
#         shape_id: ({len(shape_id)}) {shape_id}
#         \
#         """
