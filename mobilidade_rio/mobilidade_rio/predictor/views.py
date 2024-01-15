"""Views for predictor app"""
import logging

import pytz
from django.conf import settings
from rest_framework import viewsets
from rest_framework.response import Response

from mobilidade_rio.predictor.models import PredictorResult

logger = logging.getLogger("predictor view")


class PredictorViewSet(viewsets.ViewSet):
    """
    Previsão de chegada para cada ônibus ou BRT
    """

    # TODO: add pagination or use a real ModelViewSet
    def list(self, _):
        """
        Return a JSON representation of the data.
        """

        # default execution
        results = PredictorResult.objects.filter(pk=1)  # pylint: disable=E1101
        if not results.exists():
            results = {"detail": "Not found."}
            return Response(results)

        result_list = results[0].result_json['result']

        # stop_id
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
            "error": results[0].result_json["error"],
            "results" : result_list,
        }

        return Response(results)
