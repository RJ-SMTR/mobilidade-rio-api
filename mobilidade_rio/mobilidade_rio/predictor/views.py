"""Views for predictor app"""
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.response import Response
from mobilidade_rio.predictor.models import *
from mobilidade_rio.predictor.serializers import *
from mobilidade_rio.predictor.utils import *


class PredictorViewSet(viewsets.ViewSet):
    """
    Previsão de chegada para cada ônibus ou BRT
    """

    # TODO: add pagination or use a real ModelViewSet
    def list(self, request):
        """
        Return a JSON representation of the data.
        """

        # stop_code
        stop_code = self.request.query_params.get("stop_code")
        if stop_code:
            stop_code = stop_code.split(',')

        # trip_short_name
        trip_short_name = self.request.query_params.get("trip_short_name")
        if trip_short_name:
            trip_short_name = trip_short_name.split(',')

        # direction_id
        direction_id = self.request.query_params.get("direction_id")
        if direction_id:
            direction_id = stop_code.split(',')

        # debug_cols
        debug_cols = self.request.query_params.get("debug_cols")

        # Run predictor
        pred = Predictor(
            stop_code=stop_code,
            direction_id=direction_id,
            trip_short_name=trip_short_name,
            debug_cols=debug_cols
        )
        ret = pred.get_eta()

        if ret:
            ret = {
                "count": len(ret),
                "next": None,
                "previous": None,
                "results" : ret
            }
        else:
            ret = {"detail": "Not found."}

        return Response(ret)
