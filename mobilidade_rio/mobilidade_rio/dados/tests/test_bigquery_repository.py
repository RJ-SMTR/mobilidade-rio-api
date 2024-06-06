"""test_predictor"""

# pylint: disable=E0611

from ctypes import Union

from django.test import TransactionTestCase

from mobilidade_rio.dados.bigquery_repository import (
    BigqueryRepository,
    BigqueryRepositoryFailedException,
)

# from mobilidade_rio.settings.base import BASE_DIR


class TestBigqueryRepository(TransactionTestCase):
    """
    Teste unitário do BigqueryRepository

    Requisitos:
    1. O BigqueryRepository deve retornar dados para a tabela `rj-smtr.veiculo.sppo_licenciamento`
    2. Se tiver erro de query ou similar, retornar erro
    """

    is_first_run = True

    def test_sppo_success(self):
        """O teste deve retornar dados com sucesso do SPPO"""
        # act
        error_code: Union[str, None] = None
        try:
            bigquery_repository = BigqueryRepository()
            result = bigquery_repository.query("""
                SELECT * FROM `rj-smtr.veiculo.sppo_licenciamento` LIMIT 5
            """)
        except BigqueryRepositoryFailedException as exception:
            error_code = exception.info['code']

        # assert
        self.assertIsNone(error_code)
        self.assertTrue(result.size > 0)
