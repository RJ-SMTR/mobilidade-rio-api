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

        results = PredictorResult.objects.filter(pk=1)
        if not results.exists():
            results = {"detail": "Not found."}
            return Response(results)

        result_list = results[0].result_json['result']

        # stop_id
        stop_id = self.request.query_params.get("stop_id")
        if stop_id:
            result_list = [i for i in result_list if i['stop_id'] == stop_id]

        # return prediction
        results = {
            "count": len(result_list),
            "next": None,
            "previous": None,
            "results" : result_list
        }

        return Response(results)
