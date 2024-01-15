import json
import logging
from datetime import datetime
from typing import Dict, Literal, Union

from django.db.models import Model
from django.test import Client, TransactionTestCase
from django.utils import timezone

from mobilidade_rio.config_django_q.tasks import generate_prediction
from mobilidade_rio.pontos.models import Calendar


class TestPredictorE2E(TransactionTestCase):
    """
    E2e tests of Predictor

    This test will not mock realtime API, only GTFS for performance and requirement reasons.
    So it will test a real life scenario

    Requirements - #172: \
    https://github.com/RJ-SMTR/mobilidade-rio-api/issues/172#issuecomment-1887856568
    """

    fixtures = [
        f"mobilidade_rio/predictor/tests/fixtures/{t}.json" for t in
        [
            "agency",
            "calendar_dates",
            "calendar",
            "frequencies",
            "routes",
            "shapes",
            "stop_times",
            "stops",
            "trips",
        ]
    ]
    logger = logging.getLogger("[TestPredictorE2E]")

    def update_date_fields(
        self,
        model: Model,
        count_direction: Literal['up', 'down', 'same'],
        fields: Dict[str, datetime],
    ):
        """Update date fields for all items in table"""
        for index, item in enumerate(model.objects.all()):
            update_data = {}
            for field, date in fields.items():
                if count_direction == "up":
                    update_data[field] = date + timezone.timedelta(days=index)
                elif count_direction == "down":
                    update_data[field] = date - timezone.timedelta(days=index)
                else:
                    update_data[field] = date
            model.objects.filter(pk=item.pk).update(**update_data)

    def test_get_predictor_success(self):
        """
        GET: /predictor - should return valid data.

        If realtime API is off, pass this test        
        """
        # arrange
        last_year_start_date = timezone.now() - timezone.timedelta(days=60)
        last_year_end_date = timezone.now() + timezone.timedelta(days=60)
        self.update_date_fields(Calendar, "down", {
            'start_date': last_year_start_date,
            'end_date': last_year_end_date,
        })
        client = Client()

        # act
        generate_prediction()
        url = "/predictor/"
        response = client.get(url)
        data = dict(response.json())

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(data, {'detail': "Not found."})
        if data['error'] and data['error'].get('code', '').startswith("external_api-realtime-"):
            self.logger.warning("Realtime is off, ignoring test")
            return
        self.assertGreater(data['count'], 0)

    def test_get_predictor_error(self):
        """
        GET: /predictor - should return error.
        """
        # arrange
        last_year_start_date = timezone.now() + timezone.timedelta(days=60)
        last_year_end_date = timezone.now() - timezone.timedelta(days=60)
        self.update_date_fields(Calendar, "down", {
            'start_date': last_year_start_date,
            'end_date': last_year_end_date,
        })
        client = Client()

        # act
        generate_prediction()
        url = "/predictor/"
        response = client.get(url)
        data = dict(response.json())

        # assert
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(data, {'detail': "Not found."})
        self.assertIsNotNone(data['error'])
        self.assertEqual(data['count'], 0)
