"""test_predictor"""

import json
import os
from datetime import datetime
from typing import Dict, Literal
from unittest import mock

import responses
from django.db.models import Model
from django.forms import model_to_dict
from django.test import TransactionTestCase
from django.utils import timezone

from mobilidade_rio.pontos.models import Calendar, CalendarDates, Routes, Shapes, Trips
from mobilidade_rio.predictor.predictor import Predictor, PredictorFailedException
from mobilidade_rio.settings.base import BASE_DIR


class TestPredictor(TransactionTestCase):
    """
    Unit test of Predictor

    Requirements - #172: \
    https://github.com/RJ-SMTR/mobilidade-rio-api/issues/172#issuecomment-1887856568
    """

    reset_sequences = True
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

    def update_date_fields(
        self,
        model: Model,
        count_direction: Literal['up', 'down'],
        fields: Dict[str, datetime],
    ):
        """Update date fields for all items in table"""
        for index, item in enumerate(model.objects.all()):
            update_data = {}
            for field, date in fields.items():
                if count_direction == "up":
                    update_data[field] = date + timezone.timedelta(days=index)
                else:
                    update_data[field] = date - timezone.timedelta(days=index)
            model.objects.filter(pk=item.pk).update(**update_data)

    def test_predictor_empty_tables(self):
        """Predictor should fail when calendar and calendar_dates tables are empty"""
        # arrange
        Calendar.objects.all().delete()  # pylint: disable=E1101
        CalendarDates.objects.all().delete()  # pylint: disable=E1101

        # act
        error_code = None
        try:
            _ = Predictor()
        except PredictorFailedException as exception:
            error_code = exception.info['code']

        # assert
        self.assertEqual(error_code, "empty-db-tables")

    def test_predictor_no_service_today(self):
        """Predictor should fail when no service_id found today"""
        # arrange
        last_year_start_date = timezone.now() - timezone.timedelta(days=600)
        last_year_end_date = timezone.now() - timezone.timedelta(days=365)
        self.update_date_fields(
            Calendar, "down",
            {"start_date": last_year_start_date, "end_date": last_year_end_date},
        )
        self.update_date_fields(
            CalendarDates, "down",
            {"date": last_year_end_date},
        )

        # act
        error_code = None
        try:
            _ = Predictor()
        except PredictorFailedException as exception:
            error_code = exception.info['code']

        # assert
        self.assertEqual(error_code, "no-service_id-found")

    @responses.activate
    @mock.patch.dict(os.environ, {"API_REALTIME": "http://inexistent.url"})
    def test_predictor_api_realtime_failed_conn(self):
        """Predictor should fail when no request to realtime api retunred connection error"""
        # arrange
        responses.add(
            responses.GET,
            "https://dados.mobilidade.rio/gps/brt",
            status=200,
            body=json.dumps(self.mocks['api_realtime'])
        )
        # act
        error_code = None
        try:
            _ = Predictor()
        except PredictorFailedException as exception:
            error_code = exception.info['code']

        # assert
        self.assertEqual(error_code, "external_api-realtime-error-connection")

    @responses.activate
    def test_predictor_api_realtime_failed_response(self):
        """Predictor should fail when no request to realtime api retunred response error"""
        # arrange
        responses.add(
            responses.GET,
            "https://dados.mobilidade.rio/gps/brt",
            status=500,
            body='Internal server error'
        )

        # act
        error_code = None
        try:
            _ = Predictor()
        except PredictorFailedException as exception:
            error_code = exception.info['code']

        # assert
        self.assertEqual(error_code, "external_api-realtime-error-response")

    @responses.activate
    def test_predictor_api_realtime_no_results(self):
        """Predictor should fail when no request to realtime api retunred zero results"""
        # arrange
        responses.add(
            responses.GET,
            "https://dados.mobilidade.rio/gps/brt",
            status=200,
            body=json.dumps({"veiculos": []}),
        )

        # act
        error_code = None
        try:
            _ = Predictor()
        except PredictorFailedException as exception:
            error_code = exception.info['code']

        # assert
        self.assertEqual(error_code, "external_api-realtime-no_results")

    @mock.patch('mobilidade_rio.predictor.predictor.timezone')
    @responses.activate
    def test_predictor_multiple_shapes_per_trip(self, mocked_timezone):
        """Predictor should fail when multiple shapes per trip were found"""
        # arrange
        responses.add(
            responses.GET,
            "https://dados.mobilidade.rio/gps/brt",
            status=200,
            body=json.dumps(self.mocks['api_realtime'])
        )
        mocked_timezone.now.return_value = datetime(2024, 1, 5)

        new_shape = model_to_dict(
            Shapes.objects.first())  # pylint: disable=E1101
        new_shape['shape_id'] += "_clone"
        del new_shape['id']
        Shapes.objects.create(**new_shape)  # pylint: disable=E1101

        for trip in Trips.objects.all():  # pylint: disable=E1101
            new_trip = model_to_dict(trip)
            new_trip['trip_id'] += "_clone"
            new_trip['shape_id'] = new_shape['shape_id']
            new_trip['route_id'] = Routes.objects.get(  # pylint: disable=E1101
                route_id=new_trip['route_id'])
            Trips.objects.create(**new_trip)  # pylint: disable=E1101

        # act
        result = []
        error_code = None
        try:
            predictor = Predictor()
            result = predictor.run_eta()
        except PredictorFailedException as exception:
            error_code = exception.info['code']

        # assert
        self.assertEqual(len(result), 0)
        self.assertEqual(error_code, "multiple-shapes-per-trip")

    @responses.activate
    def test_predictor_no_result(self):
        """Predictor should raise exception if no result"""
        # arrange
        responses.add(
            responses.GET,
            "https://dados.mobilidade.rio/gps/brt",
            status=200,
            body=json.dumps(self.mocks['api_realtime'])
        )

        for trip in Trips.objects.all():  # pylint: disable=E1101
            trip.trip_short_name += "_clone"
            trip.save()

        # act
        result = []
        error_code = None
        try:
            predictor = Predictor()
            result = predictor.run_eta()
        except PredictorFailedException as exception:
            error_code = exception.info['code']

        # assert
        self.assertEqual(len(result), 0)
        self.assertEqual(error_code, "no_result")

    @mock.patch('mobilidade_rio.predictor.predictor.timezone')
    @responses.activate
    def test_predictor_success(self, mocked_timezone):
        """Predictor should return data successfully"""
        # arrange
        mocked_timezone.now.return_value = datetime(2024, 1, 5)
        responses.add(
            responses.GET,
            "https://dados.mobilidade.rio/gps/brt",
            status=200,
            body=json.dumps(self.mocks['api_realtime'])
        )

        new_shape = model_to_dict(
            Shapes.objects.first())  # pylint: disable=E1101
        new_shape['shape_id'] += "_clone"
        del new_shape['id']
        Shapes.objects.create(**new_shape)  # pylint: disable=E1101

        # act
        result = []
        error_code = None
        try:
            predictor = Predictor()
            result = predictor.run_eta()
        except PredictorFailedException as exception:
            error_code = exception.info['code']

        # assert
        self.assertGreater(len(result), 0)
        self.assertIsNone(error_code)
