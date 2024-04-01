"""Utils for predictor app"""
import logging
import os
import warnings
from datetime import datetime
from typing import List, Literal, TypedDict, Union

import pandas as pd
import requests
from django.db.models import Q
from django.utils import timezone
from pyproj import Transformer
from shapely.geometry import LineString, Point
from shapely.ops import snap, split, transform

from mobilidade_rio.pontos.models import (
    Calendar,
    CalendarDates,
    Shapes,
    Stops,
    StopTimes,
    Trips,
)

warnings.filterwarnings("ignore", category=RuntimeWarning)
logger = logging.getLogger("predictor")


class TPredictorETA(TypedDict):
    """Type for predictor result"""
    codigo: str
    stop_id: str
    dataHora: str
    latitude: float
    longitude: float
    velocidade: int
    d_px_to_stop: float
    direction_id: int
    trip_short_name: str
    estimated_time_arrival: float


class TPredictorInfo(TypedDict):
    """Type for predictor result info, warning or error"""
    code: str
    message: str
    type: Literal["error", "warning", "info"]
    details: dict


class TPredictorResponse(TypedDict):
    """Type for predictor response"""
    result: List[TPredictorETA]
    error: TPredictorInfo


class TPredServiceIdInfo(TypedDict):
    """Type for Predictor.service_id_info"""
    obsolete_count: int
    future_count: int
    available_today_count: int
    obsolete: List[str]
    future: List[str]
    available_today: List[str]


class PredictorFailedException(Exception):
    """When Predictor failed to run some task"""

    info: TPredictorInfo

    def __init__(self, info: TPredictorInfo):
        super().__init__(info['message'])
        self.info = info


class Predictor:  # pylint: disable=R0903
    """
    Input:
        stop_code:           1st option, easy for frontend to implement
        direction_id:        2nd option, frontend will need more steps to find it
        trip_short_name:     3rd option, user in app will need to select platform in UI
        debug_cols:          show extra cols in output, for debugging purposes

    Output:
        Dataframe with realtime API fields + ETA (Estimated Time of Arrival)

    Raises:
        PredictorFailedException
    """

    service_id_info: TPredServiceIdInfo = {
        "obsolete_count": 0,
        "future_count": 0,
        "available_today_count": 0,
        "obsolete": [],
        "future": [],
        "available_today": [],
    }

    def __init__(self, service_id=None, rt_data=None):

        # get current real time vehicle positions
        self.rt_data = self._set_realtime(rt_data)

        # get current service_id
        self.service_id = self._get_service_id(service_id)

        # default CRS transformer
        self.crs = Transformer.from_crs("epsg:4326", "epsg:31983")

    def _get_service_id(self, service_id):
        """
        Get service id from given predictor parameters.
        Also generates service_id_info
        """

        if service_id is not None:
            return service_id

        zero_counts = [i.__name__ for i in
                       [Calendar, CalendarDates, Shapes, Stops, StopTimes, Trips]
                       if i.objects.all().count() == 0]  # pylint: disable=E1101
        if len(zero_counts):
            raise PredictorFailedException({
                "type": "error",
                "code": "empty-db-tables",
                "message": f"As tabelas a seguir estão vazias no banco: {zero_counts}",
                "details": {},
            })

        today_date = timezone.now().date()

        # regular services
        weekday = today_date.strftime("%A").lower()

        regular_services_today_q = Calendar.objects.filter(  # pylint: disable=E1101
            **{weekday: 1})
        regular_services_today = list(
            regular_services_today_q.values_list("service_id", flat=True))

        # exception services
        exception_services_today_q = CalendarDates.objects.filter(  # pylint: disable=E1101
            date=today_date,
        )
        exception_services_today = list(
            exception_services_today_q.values_list("service_id", flat=True))
        exception_services_today_add = list(
            exception_services_today_q.filter(exception_type=1).values_list("service_id", flat=True))

        exception_services_today_remove_q = exception_services_today_q.filter(
            exception_type=2)
        exception_services_today_remove = list(
            exception_services_today_remove_q.values_list("service_id", flat=True))

        exception_services_today_remove_only_q = exception_services_today_remove_q.exclude(
            service_id__in=exception_services_today_add)
        exception_services_today_remove_only = list(
            exception_services_today_remove_only_q.values_list("service_id", flat=True))

        # valid services
        valid_services_today_q = Calendar.objects.filter(  # pylint: disable=E1101
            # include regular services in date range for today
            Q(
                start_date__lte=today_date,  # today > start_date
                end_date__gte=today_date,  # and today < end_date
                **{weekday: 1},  # service is active today
            ) |
            # or exception services for today
            Q(
                service_id__in=exception_services_today_add
            )
            # and ignore exception services to be removed only, for today.
            # (remove regular and not add exception)
        ).exclude(service_id__in=exception_services_today_remove_only_q.values_list(
            "service_id", flat=True))
        valid_services_today = list(
            valid_services_today_q.values_list("service_id", flat=True))

        if valid_services_today_q.count() > 1:
            # note: Predictions for trips with different shapes may be wrong, tests are needed.
            logger.info(
                "Treated services: multiple services found for today, getting first one.")
        logger.info("Services found: %s", list(
            valid_services_today_q.values_list("service_id", flat=True)))

        if valid_services_today_q.count() == 0:
            raise PredictorFailedException({
                "type": "error",
                "code": "no-service_id-found",
                "message": str(
                    "Não foram encontrados service_id para o dia de hoje"
                    + "Possíveis causas: 1. O GTFS obsoleto, há services ignorados ("
                    + f"obsoleto: {self.service_id_info['obsolete_count']}, "
                    + f"no futuro: {self.service_id_info['future_count']}, "
                    + f"disponível hoje: {self.service_id_info['available_today_count']})."),
                "details": {
                    "service_id": self.service_id_info,
                    "regular_services_today": regular_services_today,
                    "exception_services_today": exception_services_today,
                    "exception_services_today_add": exception_services_today_add,
                    "exception_services_today_remove": exception_services_today_remove,
                    "exception_services_today_remove_only": exception_services_today_remove_only,
                    "valid_services_today": valid_services_today,
                },
            })

        # service_id info

        service_before = list(regular_services_today_q.filter(
            end_date__lt=today_date).values("service_id", "end_date"))
        for i in service_before:
            i["end_date"] = i['end_date'].strftime("%Y-%m-%d")
        self.service_id_info["obsolete"] = service_before
        self.service_id_info["obsolete_count"] = len(service_before)

        service_after = list(regular_services_today_q.filter(
            start_date__gt=today_date).values("service_id", "start_date"))
        for i in service_after:
            i["start_date"] = i['start_date'].strftime("%Y-%m-%d")
        self.service_id_info["future"] = service_after
        self.service_id_info["future_count"] = len(service_after)

        service_available = list(valid_services_today_q.values_list(
            "service_id", flat=True))
        self.service_id_info["available_today"] = service_available
        self.service_id_info["available_today_count"] = len(service_available)

        return valid_services_today_q.values_list("service_id", flat=True)

    def _set_realtime(self, rt_data):
        """
        Set realtime data.
        """

        if rt_data is not None and isinstance(rt_data) == pd.DataFrame:
            return rt_data

        start = datetime.now()
        url = os.environ.get(
            "API_REALTIME", "https://dados.mobilidade.rio/gps/brt")
        elapsed_time = round((datetime.now() - start).total_seconds(), 2)
        logger.info("Request to realtime took %ss", elapsed_time)

        try:
            response = requests.get(url, timeout=5)
        except Exception as error:  # pylint: disable=W0612
            raise PredictorFailedException({
                "type": "error",
                "code": "external_api-realtime-error-connection",
                "message": f"Erro na API realtime: {error}",
                "details": {},
            }) from error

        if not response.ok:
            raise PredictorFailedException({
                "type": "error",
                "code": "external_api-realtime-error-response",
                "message": f"Erro na API realtime: {response.status_code} - {response.reason}",
                "details": {},
            })

        data = pd.DataFrame(pd.json_normalize(response.json()["veiculos"]))

        if data.empty:
            raise PredictorFailedException(
                {
                    "type": "error",
                    "code": "external_api-realtime-no_results",
                    "message": "API realtime retornou zero resultados",
                    "details": {"service_id": self.service_id_info},
                })

        logger.info("Request result length: %i", len(data))

        # rename columns
        data.rename(
            columns={"linha": "trip_short_name", "trajeto": "trip_headsign"},
            inplace=True,
        )
        data["direction_id"] = data["sentido"].apply(
            lambda x: 1 if x == "volta" else 0)

        # conver unix to datetime
        data["dataHora"] = (data["dataHora"] /
                            1000).apply(datetime.fromtimestamp)
        data["dataHora"] = data["dataHora"].astype(str)

        return data

    def _get_shape_id(self, trip_short_name, direction_id, service_ids_for_today) -> Union[str, None]:
        """
        Get unique shape in trips given unique (trip_short_name, direction_id) \
            + any service_id

        Parameters
        ---
        ``direction_id``(str): Field to filter as unique combination

        ``trip_short_name``(str): Field to filter as unique combination

        ``service_ids_for_today``(list): Any treated service_id, \
            it must agree with date exceptions (calendar_dates) or normal services (calendar)

        Return
        ---
        Unique shape_id for combination of fields in trips
        """

        trips = Trips.objects.filter(  # pylint: disable=E1101
            trip_short_name=trip_short_name,
            direction_id=direction_id,
            service_id__in=list(service_ids_for_today),
        )

        shapes_q = trips.distinct("shape_id")
        shapes = list(shapes_q.values_list("shape_id", flat=True))
        shapes_objs = list(shapes_q.values('shape_id', 'trip_id', 'block_id'))

        if len(shapes_q) > 1:
            raise PredictorFailedException({
                "type": "error",
                "code": "multiple-shapes-per-trip",
                "message": f"Foram encontradas mais de uma trip por shape_id ({len(shapes)}).",
                "details": {
                    'trips': {"count": len(shapes),
                              "found": shapes_objs},
                },
            })
        if len(shapes_q) == 0:
            return None

        return shapes[0]

    def _split_shape(self, shape, break_pt, part=0):
        """
        Splits a shape based on a point. By default gets only the first part.
        """
        return split(snap(shape, break_pt, 1e-8), break_pt).geoms[part]

    def _get_shape_lenght(self, shape, unit="km"):
        """
        Calculates the shape lenght over the choosen CRS. To change the CRS,\
            check the attribute self.crs.
        """
        # print([s for s in shape if not s])
        lenght = transform(self.crs.transform, shape).length
        if unit == "km":
            return lenght / 1000
        return lenght

    def _get_trip_eta(self, shape, stop, positions) -> TPredictorETA:
        """
        Gets ETA of all vehicle to a stop, operating on a specific trip.
        """

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
        stop_pt = Point(stop.stop_lat, stop.stop_lon)
        stop_pt_proj = shape.interpolate(shape.project(stop_pt))
        positions["d_start_to_stop"] = self._get_shape_lenght(
            self._split_shape(shape, stop_pt_proj)
        )

        # calculate distance from vehicle to stop (diff from above ones)
        positions["d_px_to_stop"] = positions.d_start_to_stop - \
            positions.d_start_to_px

        # set expected minimum speed
        positions["velocidade"] = (
            positions["velocidade"]
            .fillna(0)
            .apply(lambda x: 30 if float(x) < 30 else float(x))
        )

        # convert to eta
        positions["estimated_time_arrival"] = positions.apply(
            lambda x: 60 * x.d_px_to_stop / x.velocidade,
            axis=1,
        )
        positions["stop_id"] = stop.stop_id

        cols = [
            "codigo",                   # pk
            "dataHora",                 # created at
            "latitude",                 # current vehicle lat
            "longitude",                # current vehicle lon
            "velocidade",
            "trip_short_name",          # linha
            "direction_id",             # 0, 1
            "estimated_time_arrival",   # in minutes
            "stop_id",                  # current stop_id children (platform)
            "d_px_to_stop",             # for debug - distance from bus to stop destination
        ]

        return positions[cols].to_dict(orient="records")

    def run_eta(self):
        """
        Runs ETA of all vehicle to all stops on the current given trip and direction.

        Note: if takes a lot of time, create shape_w_stops and \
            filter only stop_ids between vehicle positions
        """

        # get all current trips
        inputs = (
            self.rt_data[["trip_short_name", "direction_id"]]
            .drop_duplicates()
            .to_dict(orient="records")
        )

        result = []
        shapes_found = []
        stops_found = []
        for params in inputs:

            trip_short_name = params["trip_short_name"]
            direction_id = params["direction_id"]

            # filter vehicles for the given trip
            positions = self.rt_data.loc[
                (self.rt_data.trip_short_name == trip_short_name)
                & (self.rt_data.direction_id == direction_id)
            ].copy()

            if len(positions) == 0:
                return []

            shape_id = self._get_shape_id(
                trip_short_name, direction_id, self.service_id)
            if shape_id is None:
                continue

            shapes_found += [shape_id]
            shape = pd.DataFrame(
                Shapes.objects.filter(shape_id=shape_id).values())  # pylint: disable=E1101

            # calculate ETA for all stops of the trip

            stop_ids = list(StopTimes.objects.filter(  # pylint: disable=E1101
                trip_id__trip_short_name=trip_short_name,
                trip_id__direction_id=direction_id
            ).filter(~Q(stop_sequence=0)).values_list("stop_id", flat=True))
            stops_found += list(set(stop_ids))
            stops = Stops.objects.filter(  # pylint: disable=E1101
                stop_id__in=stop_ids,
            )

            for stop in stops:
                result += self._get_trip_eta(
                    positions=positions,
                    stop=stop,
                    shape=LineString(
                        list(
                            zip(shape['shape_pt_lat'], shape['shape_pt_lon'])
                        )
                    ),  # .wkt
                )
            # break

        if len(result) == 0:
            service_obsolete = self.service_id_info["obsolete"]
            service_future = self.service_id_info["future"]
            message = []
            i = 1
            if any([service_obsolete, service_future]):
                message += [str(
                    f"{i}. O GTFS obsoleto, há services ignorados ("
                    + f"obsoleto: {self.service_id_info['obsolete_count']}, "
                    + f"no futuro: {self.service_id_info['future_count']}, "
                    + f"disponível hoje: {self.service_id_info['available_today_count']})"
                )]
                i += 1

            if len(shapes_found) == 0:
                message += [f"{i}. Não foram encontrados shapes."]
                i += 1

            if len(stops_found) == 0:
                message += [f"{i}. Não foram encontrados stops."]
                i += 1

            if len(message) > 0:
                message = f"Possíveis causas: {'; '.join(message)}."

            raise PredictorFailedException({
                'type': "error",
                'code': "no_result",
                'message': str("Sem resultados." + message),
                'details': {'service_id': self.service_id_info, 'shapes_found': len(shapes_found)}
            })

        return result
