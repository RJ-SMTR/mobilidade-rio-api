"""Views for predictor app"""
import json
import logging
import math
from datetime import timedelta, datetime

import pytz
from django.conf import settings
from django.utils import timezone
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

        unchanged_timeout_secs = 60 * 5

        results = PredictorResult.objects.filter(pk=1)  # pylint: disable=E1101
        last_check = PredictorResult.objects.filter(  # pylint: disable=E1101
            pk=2)

        # error: no_result
        if not results.exists():
            # no result more than 5 minutes
            last_check_count_seconds = 0 if not last_check.exists() else (
                timezone.now() - last_check[0].last_modified).total_seconds()
            if (last_check and last_check_count_seconds >= unchanged_timeout_secs):
                error_message = {
                    'code': "no_result-unchanged-timeout",
                    'message': "Sem alterações no banco do preditor há mais de " +
                    f"{math.floor(unchanged_timeout_secs/60)} minutos.",
                    "lastCheck": last_check[0].last_modified,
                    "lastCheckCount": str(timedelta(seconds=int(last_check_count_seconds))),
                    "lastCheckCountSeeconds": int(last_check_count_seconds),
                }
                return Response(error_message, status=500)

            PredictorResult.objects.update_or_create(  # pylint: disable=E1101
                pk=2,
                defaults={
                    'result_json': {'about': "Save last result check"},
                }
            )

            # no result
            error_message = {
                'code': "no_result",
                'message': "Resultado do preditor não encontrado no banco.",
                "lastCheck": last_check[0].last_modified if last_check.exists() else None,
                "lastCheckCount": str(timedelta(seconds=int(last_check_count_seconds))
                                      ) if last_check.exists() else None,
                "lastCheckCountSeconds": int(last_check_count_seconds
                                             ) if last_check.exists() else None,
            }
            return Response(error_message, status=404)

        if last_check.exists():
            last_check.delete()

        last_update = results[0].last_modified.astimezone(
            pytz.timezone(settings.TIME_ZONE))

        result_data = results[0].result_json['result']
        result_error = results[0].result_json['error']

        # error: result-unchanged more than 5 minutes
        last_update_count_seconds = (
            timezone.now() - results[0].last_modified).total_seconds()
        if last_update_count_seconds >= unchanged_timeout_secs:
            error_message = {
                'code': "result-unchanged-timeout",
                'message': "Sem alterações no banco do preditor há mais de " +
                f"{math.floor(unchanged_timeout_secs/60)} minutos.",
                'data': result_data,
                'error': result_error,
                'lastUpdate': last_update,
                'lastUpdateCount': str(timedelta(seconds=int(last_update_count_seconds))),
                'lastUpdateCountSeconds': int(last_update_count_seconds),
            }
            return Response(error_message, status=500)

        # error: predictor-error
        if result_error:
            error_message = {
                'code': "predictor-error",
                'message': "O preditor retornou erro.",
                "error": results[0].result_json["error"],
            }
            return Response(error_message, status=500)

        # query filter
        stop_id = self.request.query_params.get("stop_id")
        if stop_id:
            result_data = [i for i in result_data if i['stop_id'] == stop_id]

        # return prediction

        response_data = {
            "count": len(result_data),
            "next": None,
            "previous": None,
            "lastUpdate": last_update,
            "lastUpdateCount": str(timedelta(seconds=int(last_update_count_seconds))),
            "lastUpdateCountSeconds": int(last_update_count_seconds),
            "error": results[0].result_json["error"],
            "results": result_data,
        }

        return Response(response_data)


class PredictorTestViewSet(viewsets.ViewSet):
    """
    Versão de teste do endpoint `/predictor`
    """

    def list(self, _):
        """
        Return a JSON representation of the data.
        """

        unchanged_timeout_secs = 60 * 5

        results = PredictorResult.objects.filter(pk=1)  # pylint: disable=E1101
        last_check = PredictorResult.objects.filter(  # pylint: disable=E1101
            pk=2)

        # error: no_result
        if not results.exists():
            # no result more than 5 minutes
            last_check_count_seconds = 0 if not last_check.exists() else (
                timezone.now() - last_check[0].last_modified).total_seconds()
            results = [PredictorResult()]
            # if (last_check and last_check_count_seconds >= unchanged_timeout_secs):
            #     error_message = {
            #         'code': "no_result-unchanged-timeout",
            #         'message': "Sem alterações no banco do preditor há mais de " +
            #         f"{math.floor(unchanged_timeout_secs/60)} minutos.",
            #         "lastCheck": last_check[0].last_modified,
            #         "lastCheckCount": str(timedelta(seconds=int(last_check_count_seconds))),
            #         "lastCheckCountSeeconds": int(last_check_count_seconds),
            #     }
            #     return Response(error_message, status=500)

            PredictorResult.objects.update_or_create(  # pylint: disable=E1101
                pk=2,
                defaults={
                    'result_json': {'about': "Save last result check"},
                }
            )

            # no result
            error_message = {
                'code': "no_result",
                'message': "Resultado do preditor não encontrado no banco.",
                "lastCheck": last_check[0].last_modified if last_check.exists() else None,
                "lastCheckCount": str(timedelta(seconds=int(last_check_count_seconds))
                                      ) if last_check.exists() else None,
                "lastCheckCountSeconds": int(last_check_count_seconds
                                             ) if last_check.exists() else None,
            }
            return Response(error_message, status=404)

        if last_check.exists():
            last_check.delete()

        last_update = results[0].last_modified.astimezone(
            pytz.timezone(settings.TIME_ZONE))

        result_data = results[0].result_json.get('result', None)
        result_error = results[0].result_json.get('error', None)

        # error: result-unchanged more than 5 minutes
        last_update_count_seconds = (
            timezone.now() - results[0].last_modified).total_seconds()
        # if last_update_count_seconds >= unchanged_timeout_secs:
        #     error_message = {
        #         'code': "result-unchanged-timeout",
        #         'message': "Sem alterações no banco do preditor há mais de " +
        #         f"{math.floor(unchanged_timeout_secs/60)} minutos.",
        #         'data': result_data,
        #         'error': result_error,
        #         'lastUpdate': last_update,
        #         'lastUpdateCount': str(timedelta(seconds=int(last_update_count_seconds))),
        #         'lastUpdateCountSeconds': int(last_update_count_seconds),
        #     }
        #     return Response(error_message, status=500)

        # error: predictor-error
        if result_error:
            error_message = {
                'code': "predictor-error",
                'message': "O preditor retornou erro.",
                "error": results[0].result_json["error"],
            }
            return Response(error_message, status=500)

        # dev: error if minute is odd
        if datetime.now().minute % 2 == 1:
            error_message = {
                'code': "dev-error",
                'message': "Este é um exemplo de erro. "
                + "O minuto atual ({datetime.now().minute}) é ímpar. "
                + "Caso o código de erro seja 'predictor-error' "
                + "o campo 'error' terá informações como neste exemplo.",
                'lastUpdate': last_update,
                'lastUpdateCount': str(timedelta(seconds=int(last_update_count_seconds))),
                'lastUpdateCountSeconds': int(last_update_count_seconds),
                "error": {
                    "type": "error",
                    "code": "external_api-realtime-error-response",
                    "message": "Erro na API realtime: 500 - Internal server error",
                    "details": {},
                }
            }
            return Response(error_message, status=500)

        # query filter
        stop_id = self.request.query_params.get("stop_id")
        if stop_id:
            result_data = [i for i in result_data if i['stop_id'] == stop_id]

        # return prediction
        response_data = {
            "count": len(result_data),
            "next": None,
            "previous": None,
            "lastUpdate": last_update,
            "lastUpdateCount": str(timedelta(seconds=int(last_update_count_seconds))),
            "lastUpdateCountSeconds": int(last_update_count_seconds),
            "error": results[0].result_json.get("error", None),
            "results": result_data,
        }

        return Response(response_data)
