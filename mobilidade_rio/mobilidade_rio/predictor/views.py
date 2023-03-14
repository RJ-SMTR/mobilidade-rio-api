"""Views for predictor app"""
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.response import Response
from mobilidade_rio.predictor.models import *
from mobilidade_rio.predictor.serializers import *
from mobilidade_rio.predictor.utils import *
from mobilidade_rio.predictor.models import PredictorResult
import json
from django.core import serializers
import logging


logger = logging.getLogger("[test]")


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
        # stop_id = self.request.query_params.get("stop_id")
        # if not stop_id:
        #     return Response({"error": "stop_id is required."})

        # trip_short_name
        # trip_short_name = self.request.query_params.get("trip_short_name")
        # if trip_short_name:
        #     trip_short_name = trip_short_name.split(',')

        # direction_id = self.request.query_params.get("direction_id")
        # if direction_id:
        #     direction_id = stop_id.split(',')

        # debug_cols
        # debug_cols = self.request.query_params.get("debug_cols")

        # Run predictor
        results = PredictorResult.objects.filter(pk=1)
        if results.exists():
            results = results[0].result_json['result']
            results = {
                "count": len(results),
                "next": None,
                "previous": None,
                "results" : results
            }
        else:
            results = {"detail": "Not found."}

        return Response(results)
