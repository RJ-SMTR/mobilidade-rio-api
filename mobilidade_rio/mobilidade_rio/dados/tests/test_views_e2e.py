"""test_views"""

import json
from unittest import mock

from django.test import Client, TransactionTestCase
from django.utils import timezone

from mobilidade_rio.predictor.models import PredictorResult
from mobilidade_rio.settings.base import BASE_DIR


class TestViewsE2E(TransactionTestCase):
    """
    Unit test of predictor.views

    Test different scenatrios of views

    Requirements - #172: \
    https://github.com/RJ-SMTR/mobilidade-rio-api/issues/172#issuecomment-1892673761
    """

    reset_sequences = True
    mocks = {
        'api_realtime': {}
    }
    is_first_run = True

    def setUp(self):
        if self.is_first_run:
            self.before_all()
            self.is_first_run = False

    def before_all(self):
        """Run it once, before all tests"""

    def test_dados_gps_sppo(self):
        """Predictor should return 200 if valid result"""
        # arrange
        PredictorResult.objects.create(  # pylint: disable=E1101
            pk=1,
            result_json={
                'result': [{'a': 1}],
                'error': None,
            }
        )

        # act
        url = "/dados/gps/sppo"
        client = Client()
        response = client.get(url)

        # assert
        self.assertEqual(response.status_code, 200)
