"""tests for django_q tasks"""

from unittest import mock

from django.test import TransactionTestCase

from mobilidade_rio.config_django_q.tasks import generate_prediction  # pylint: disable=E0401,E0611
from mobilidade_rio.predictor.models import PredictorResult
from mobilidade_rio.predictor.predictor import PredictorFailedException


class TestGeneratePrediction(TransactionTestCase):
    """
    Tests for method generate_prediction() method

    Requirements - #172: \
    https://github.com/RJ-SMTR/mobilidade-rio-api/issues/172#issuecomment-1887856568
    """

    @mock.patch('mobilidade_rio.config_django_q.tasks.Predictor.__init__')
    @mock.patch('mobilidade_rio.config_django_q.tasks.Predictor.run_eta')
    @mock.patch('mobilidade_rio.config_django_q.tasks.PredictorResult.objects.filter')
    def test_generate_prediction_remove_duplicates(
        self,
        mock_pr_filter: mock.Mock,
        mock_run_eta: mock.Mock,
        mock_init: mock.Mock,
    ):
        """When has two PredictorResults pk=1, remove duplicates and save result"""
        # arrange
        mock_delete = mock.Mock()
        class MockPredictorResultQS:  # pylint: disable=C0115
            def __len__(self):
                return 2

            def delete(self):  # pylint: disable=C0116
                pass
        MockPredictorResultQS.delete = mock_delete

        mock_init.return_value = None
        mock_run_eta.return_value = [{'key': "value"}]
        mock_pr_filter.return_value = MockPredictorResultQS()

        # act
        generate_prediction()

        # assert
        mock_delete.assert_called()
        results = PredictorResult.objects.all()  # pylint: disable=E1101
        self.assertEqual(results.count(), 1)
        self.assertEqual(results[0].result_json, {
            'error': None,
            'result': [{'key': "value"}],
        })

    @mock.patch('mobilidade_rio.config_django_q.tasks.Predictor.__init__')
    @mock.patch('mobilidade_rio.config_django_q.tasks.Predictor.run_eta')
    def test_generate_prediction_success(
        self,
        mock_run_eta: mock.Mock,
        mock_init: mock.Mock,
    ):
        """Save or update success result"""
        # arrange
        mock_init.return_value = None
        mock_run_eta.return_value = [{'key': "value"}]

        # act
        generate_prediction()

        # assert
        results = PredictorResult.objects.all()  # pylint: disable=E1101
        self.assertEqual(results.count(), 1)
        self.assertEqual(results[0].result_json, {
            'result': [{'key': "value"}],
            'error': None,
        })

    @mock.patch('mobilidade_rio.config_django_q.tasks.Predictor.__init__')
    @mock.patch('mobilidade_rio.config_django_q.tasks.Predictor.run_eta')
    def test_generate_prediction_error(
        self,
        mock_run_eta: mock.Mock,
        mock_init: mock.Mock,
    ):
        """Save or update success result"""
        # arrange
        error_data = {
            'code': "mock_code",
            'message': "some error",
            'type': 'error',
            'details': {},
        }
        mock_init.return_value = None
        mock_run_eta.side_effect = PredictorFailedException(error_data)

        # act
        generate_prediction()

        # assert
        results = PredictorResult.objects.all()  # pylint: disable=E1101
        self.assertEqual(results.count(), 1)
        self.assertEqual(results[0].result_json, {
            'result': [],
            'error': error_data,
        })
