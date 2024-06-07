"""
Equivalente a uma camada service

A Camada utils contém uma classe por endpoint
"""
import json
from datetime import date
from datetime import datetime as dt
from datetime import timedelta
from typing import Literal, TypedDict
from venv import logger

import pandas as pd
import requests
from numpy import number

from mobilidade_rio.dados.bigquery_repository import BigqueryRepository


class DadosUtilsInfo(TypedDict):
    """Type for predictor result info, warning or error"""
    code: str
    http_status_code: number
    message: str
    type: Literal["error", "warning", "info"]
    details: dict


class DadosUtilsFailedException(Exception):
    """When Predictor failed to run some task"""

    info: DadosUtilsInfo

    def __init__(self, info: DadosUtilsInfo):
        super().__init__(info['message'])
        self.info = info


class DadosGpsSppoUtils:
    """
    Requisitos: 
    ## Tarefas:

    ### 1. Pegar dados do SPPO

    Link SPPO: https://dados.mobilidade.rio/gps/sppo

    Na API o `id_veiculo` = "ordem"

    Parâmetros da API externa:
    - dataInicial (`yyyy-MM-dd HH:mm:ss`)
    - dataFinal (`yyyy-MM-dd HH:mm:ss`)

    Parâmetros do Django:
    - data_inicial (`yyyy-MM-dd HH:mm:ss`)
    - data_final (`yyyy-MM-dd HH:mm:ss`)

    ### 2. Relacionar dados SPPO com colunas bigquery

    Tabela do bigquery: `rj-smtr.veiculo.sppo_licenciamento`

    Colunas: Chassi, Carroceria, AnoFabricação, TipoVeículo

    O ID é `id_veiculo`
    """

    request_timeout = 30
    bigquery_repository: BigqueryRepository = None
    data_format = 'yyyy-mm-dd hh-mm-ss'

    def run(self, data_inicial='', data_final=''):
        """Executar tarefa completa"""
        self._validate_params(data_inicial, data_final)
        sppo_bq = self._get_sppo_bigquery(data_final, data_final)
        sppo_api = self._get_sppo_api(data_inicial, data_final)
        sppo_join = self._join_sppo_api_bigquery(sppo_api, sppo_bq)
        return sppo_join

    def _validate_params(self, data_inicial='', data_final=''):
        if not self._is_valid_datetime(data_inicial) or\
                not self._is_valid_datetime(data_final):
            raise DadosUtilsFailedException({
                "type": "error",
                "code": "dados_gps_sppo-error-params",
                "http_status_code": 422,
                "message": "data_inicial e data_final são obrigatórios "
                "e devem ter o formato: 'yyyy-mm-dd HH-MM-ss'",
                "details": {},
            })

        data_inicial_date = date(
            int(data_inicial[:4]), int(data_inicial[5:7]), int(data_inicial[8:10]))
        data_final_date = date(
            int(data_final[:4]), int(data_final[5:7]), int(data_final[8:10]))
        data_diff = data_final_date - data_inicial_date
        if data_diff.seconds > 60*5:
            raise DadosUtilsFailedException({
                "type": "error",
                "code": "dados_gps_sppo-error-params",
                "http_status_code": 422,
                "message": "A diferença de data deve ser <= 5 minutos",
                "details": {},
            })

    def _is_valid_datetime(self, date_str: str) -> bool:
        """
        Checks if a string is a valid date and time in the format 'yyyy-mm-dd HH-MM-ss'.

        Example: '2024-01-29 13:59:59' (24h)
        """
        try:
            dt.strptime(date_str, r'%Y-%m-%d %H:%M:%S')
            return True
        except ValueError:
            return False

    def _get_sppo_api(self, data_inicial='', data_final=''):
        """
        Obter dados da API SPPO

        Args:
        - data_inicial: `yyyy-MM-dd HH:mm:ss`
        - data_final: `yyyy-MM-dd HH:mm:ss`
        """
        start = dt.now()
        url = "https://dados.mobilidade.rio/gps/sppo"

        # Get params
        params = {'dataInicial': data_inicial, 'dataFinal': data_final}
        if not params["dataInicial"]:
            del params["dataInicial"]
        if not params["dataFinal"]:
            del params["dataFinal"]
        if not params:
            params = None

        # Run
        try:
            response = requests.get(
                url, timeout=self.request_timeout, params=params)
        except Exception as error:  # pylint: disable=W0612
            raise DadosUtilsFailedException({
                "type": "error",
                "code": "dados_gps_sppo-error-connection",
                "message": f"Erro na API GPS: {error}",
                "details": {},
            }) from error

        if not response.ok:
            raise DadosUtilsFailedException({
                "type": "error",
                "code": "dados_gps_sppo-error-response",
                "message": f"Erro na API GPS: {response.status_code} - {response.reason}",
                "details": {},
            })

        response_data = json.loads(response.text)
        if isinstance(response_data, dict):
            if response_data.get('RetornoOK', False) is False:
                error_message = response_data.get("DescricaoErro", "")
                raise DadosUtilsFailedException({
                    "type": "error",
                    "code": "dados_gps_sppo-error-response-data",
                    "http_status_code": 500,
                    "message": f"Erro na API GPS SPPO: {error_message}",
                    "details": {},
                })

        # Treat
        data = pd.DataFrame(pd.json_normalize(response.json()))

        # Log
        elapsed_time = round((dt.now() - start).total_seconds(), 2)
        logger.info("Requisição para o SPPO durou %ss", elapsed_time)

        return data

    def _get_sppo_bigquery(self, data_inicial="", data_final=""):
        """
        Obter dados SPPO do Bigquery

        O Bigquery as vezes não tem dados para o dia de hoje,
        por isso pegamos também o dia anterior como `data_inicio`.
        """
        bigquery = BigqueryRepository()
        where = ""

        if data_inicial:
            day = date(
                int(data_inicial[:4]),   # yyyy
                int(data_inicial[5:7]),  # mm
                int(data_inicial[8:10])  # dd
            )
            before = day - timedelta(days=1)
            where += f"data = '{before.strftime(r'%Y-%m-%d')}' "

        if data_final:
            if where:
                where += "OR "
            where += f"data = '{data_final[:10]}' "

        query = "SELECT * FROM `rj-smtr.veiculo.sppo_licenciamento` "
        if where:
            query += f"WHERE {where}"
        query += " LIMIT 10000"
        data = bigquery.query(query)
        return data

    def _join_sppo_api_bigquery(self, sppo_api: pd.DataFrame, sppo_bq: pd.DataFrame):
        """
        Pegar a tabela API SPPO e adicionar colunas do Bigquery

        Colunas: Chassi, Carroceria, AnoFabricação, TipoVeículo
        """

        try:
            join_df = sppo_api.merge(
                sppo_bq[["id_veiculo", "carroceria",
                        "ano_fabricacao", "tipo_veiculo"]],
                left_on="ordem",
                right_on="id_veiculo",
                how="inner")
            join_df = join_df.drop(["id_veiculo"], axis=1)
            return join_df

        except pd.errors.MergeError as exception:
            raise DadosUtilsFailedException({
                "type": "error",
                "code": "dados_gps_sppo-error-response-data",
                "http_status_code": 500,
                "message": "Internal server error",
                "details": {
                    "message": str(exception)
                },
            }) from exception
