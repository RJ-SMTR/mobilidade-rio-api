"""test_predictor"""

# pylint: disable=E0611
# pylint: disable=E0401
# pylint: disable=W0212

import os
from ctypes import Union

import pandas as pd
from django.test import TransactionTestCase

from mobilidade_rio.dados.utils import (
    DadosGpsSppoUtils,
    DadosUtilsFailedException,
    DadosUtilsInfo,
)

# from mobilidade_rio.settings.base import BASE_DIR


class TestGetSppoBigqueryUtils(TransactionTestCase):
    """
    Teste unitário do GetSppoBigqueryUtils

    Requisitos:
    1. Deve obter os dados da API do SPPO com sucesso
    2. Deve funcionar o SPPO com realtime
    3. Retornar o resultado tratado para a View
    """

    is_first_run = True

    def test_sppo_success(self):
        """
        Deve obter dados da API do SPPO com sucesso

        Isto não irá usar filtros pois o objetivo é saber se retornará dados, e não vazio.
        """
        # act
        error = None
        result: pd.DataFrame = None
        try:
            get_sppo_utils = DadosGpsSppoUtils()
            result = get_sppo_utils._get_sppo_api()
        except DadosUtilsFailedException as exception:
            error = exception.info
            print("ERRO:")
            print(error)

        # assert
        self.assertIsNone(error)
        self.assertTrue(result.size > 0)

    def test_sppo_error_response_data(self):
        """
        Ao obter dados da API do SPPO deve repassar o erro de parâmetro da API externa como uma exceção.

        Isso irá testar:
        - O filtro: caso dê erro a diferença de horário foi passada para a API externa
        - O retorno de parâmeto inválido da API externa

        Exemplo:

            Retorno de parâmetro inválido pela API externa:

            Status: 200

            ```json
            {
                "RetornoOK":false,
                "IdentificacaoLogin":null,
                "DescricaoErro":"O intervalo entre as datas não pode ser maior do que 1 uma hora",
                "Empresas":null
            }
            ```

            O service deve transformar isso em Exceção para mandar para o frontend na View.
        """
        # act
        error_code: Union[str, None] = None
        try:
            get_sppo_utils = DadosGpsSppoUtils()
            get_sppo_utils._get_sppo_api(
                '2024-05-10 00:00:00', '2024-05-11 00:00:00')
        except DadosUtilsFailedException as exception:
            error_code = exception.info['code']

        # assert
        self.assertEqual(error_code, 'dados_gps_sppo-error-response-data')

    def test_join_sppo_api_bigquery(self):
        """
        Espera-se juntar a tabela SPPO com o Bigquery.
        """
        # arrange
        this_folder = os.path.dirname(__file__)
        sppo_bq = pd.read_json(f'{this_folder}/data/sppo_bq.json')
        sppo_api = pd.read_json(f'{this_folder}/data/sppo_api.json')
        expected_cols = {
            "ordem", "latitude", "longitude", "datahora", "velocidade",
            "linha", "datahoraenvio", "datahoraservidor", "carroceria",
            "ano_fabricacao", "tipo_veiculo"
        }

        # act
        error: DadosUtilsInfo = None
        sppo_join: pd.DataFrame = None
        try:
            get_sppo_utils = DadosGpsSppoUtils()
            sppo_join = get_sppo_utils._join_sppo_api_bigquery(
                sppo_api, sppo_bq)
        except DadosUtilsFailedException as exception:
            error = exception.info
            print("ERRO:")
            print(error)

        # assert
        self.assertIsNone(error)
        self.assertEqual(set(sppo_join.columns.to_list()), expected_cols)
        self.assertTrue(sppo_join.size > 0)
