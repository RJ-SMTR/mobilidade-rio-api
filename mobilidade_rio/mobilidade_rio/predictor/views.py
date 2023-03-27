"""Views for predictor app"""
from rest_framework.response import Response
from rest_framework import viewsets
from mobilidade_rio.predictor.models import *
from mobilidade_rio.predictor.serializers import *
from mobilidade_rio.predictor.utils import *
from mobilidade_rio.predictor.models import PredictorResult
from django.conf import settings
import pytz


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
        pred = self.request.query_params.get("pred")
        if pred:
            results = {"pred": "done."}
            return Response(results)

        stop_id = self.request.query_params.get("stop_id")
        if stop_id:
            result_list = [i for i in result_list if i['stop_id'] == stop_id]

        # return prediction
        last_modified = results[0].last_modified.astimezone(pytz.timezone(settings.TIME_ZONE))

        results = {
            "count": len(result_list),
            "next": None,
            "previous": None,
            "lastUpdate": last_modified,
            "results" : result_list
        }

        return Response(results)
