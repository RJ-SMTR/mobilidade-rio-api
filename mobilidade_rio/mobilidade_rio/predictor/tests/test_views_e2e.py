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
        api_realtime_path = f"{BASE_DIR}/predictor/tests/data/api_realtime.json".replace(
            "\\", "/")
        with open(api_realtime_path, encoding="utf8") as f:
            self.mocks['api_realtime'] = json.load(f)

    def test_predictor_success(self):
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
        url = "/predictor/"
        client = Client()
        response = client.get(url)

        # assert
        self.assertEqual(response.status_code, 200)

    def test_predictor_no_result_found(self):
        """Predictor should return 404 if no PredictorResult found in db is under 5 minutes"""
        # arrange

        # act
        url = "/predictor/"
        client = Client()
        response = client.get(url)

        # assert
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()['code'], "no_result")

    def test_predictor_no_result_timeout(self):
        """Predictor should return 500 if no PredictorResult found in db after 5 minutes"""
        # arrange
        now = timezone.now()
        last_minutes = now - timezone.timedelta(minutes=5, seconds=1)

        with mock.patch.object(timezone, 'now', return_value=last_minutes):
            PredictorResult.objects.create(  # pylint: disable=E1101
                pk=2,
                result_json={'dev': 'last check'},
            )

        # act
        url = "/predictor/"
        client = Client()
        response = client.get(url)

        # assert
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['code'],
                         "no_result-unchanged-timeout")

    def test_predictor_result_timeout(self):
        """Predictor should return if valid PredictorResult is not updated after 5 minutes"""
        # arrange
        now = timezone.now()
        last_minutes = now - timezone.timedelta(minutes=5)

        with mock.patch.object(timezone, 'now', return_value=last_minutes):
            PredictorResult.objects.create(  # pylint: disable=E1101
                pk=1,
                result_json={
                    'result': [],
                    'error': {'code': "mock-error"},
                }
            )

        # act
        url = "/predictor/"
        client = Client()
        response = client.get(url)

        # assert
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['code'], "result-unchanged-timeout")

    def test_predictor_error(self):
        """Predictor should return 500 if no PredictorResult found in db after 5 minutes"""
        # arrange
        PredictorResult.objects.create(  # pylint: disable=E1101
            pk=1,
            result_json={
                'result': [],
                'error': {'code': "mock-error"},
            }
        )

        # act
        url = "/predictor/"
        client = Client()
        response = client.get(url)

        # assert
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()['code'], "predictor-error")
