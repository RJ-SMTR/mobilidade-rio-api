from ast import Dict, List
import logging
from datetime import datetime as dt
from rest_framework.response import Response
from rest_framework import viewsets

from mobilidade_rio.dados.utils import (
    DadosGpsSppoUtils,
    DadosUtilsFailedException,
)

# Create your views here.


class SppoViewSet(viewsets.ViewSet):
    """
    Return data from SPPO with extra columns.

    Parameters:

    - **data_inicio** : mandatory

        example: `2024-01-29 13:59:59` 

        format: `yyyy-mm-dd HH:MM:ss`

    - **data_fim** : mandatory

        example: `2024-01-29 13:59:59`

        format: `yyyy-mm-dd HH:MM:ss`

    """

    logger = logging.getLogger('DadosGpsSppoViewSet')

    def list(self, _):
        """GET"""
        start = dt.now()

        params = self.request.query_params
        utils = DadosGpsSppoUtils()
        error: DadosUtilsFailedException = None
        result_list: List[Dict[str, any]] = []

        try:
            result = utils.run(
                data_inicial=params.get("data_inicial", ""),
                data_final=params.get("data_final", ""),
            )
            result_list = result.to_dict(orient='records')
        except DadosUtilsFailedException as exception:
            error = exception

        error_info = None
        if error:
            error_info = error.info

        # Log
        elapsed_time = round((dt.now() - start).total_seconds(), 2)
        self.logger.info("A requisição da view durou %ss", elapsed_time)

        response_data = {
            "error": error_info,
            "count": len(result_list),
            "results": result_list,
        }
        status_code = 200
        if error_info:
            status_code = error_info["http_status_code"]

        return Response(response_data, status_code)
