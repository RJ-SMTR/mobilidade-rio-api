"""Views for predictor app"""
import logging
from rest_framework.response import Response
from rest_framework import viewsets
from mobilidade_rio.config_django_q.tasks import generate_prediction
from mobilidade_rio.predictor.models import *
from mobilidade_rio.predictor.serializers import *
from mobilidade_rio.predictor.models import PredictorResult
from django.conf import settings
import pytz


logger = logging.getLogger("predictor view")


class PredictorViewSet(viewsets.ViewSet):
    """
    Previsão de chegada para cada ônibus ou BRT
    """

    # TODO: add pagination or use a real ModelViewSet
    def list(self, request):
        """
        Return a JSON representation of the data.
        """

        # dev params
        if settings.SETTINGS_MODULE.rsplit('.',1)[-1] not in ("dev", "stag", "prod"):
            run = request.query_params.get("run")
            if run:
                logger.info('run: Generating prediction manually')
                generate_prediction()
        
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
