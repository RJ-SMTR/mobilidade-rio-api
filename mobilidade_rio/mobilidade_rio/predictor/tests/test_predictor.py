"""test_predictor"""

from django.test import TestCase
from mobilidade_rio.predictor.predictor import Predictor


class TestPredictor(TestCase):
    """TestPredictor"""

    def test_predictor_init_success(self):
        """Test if predictor initializes successfully"""
        try:
            _ = Predictor()
        except Exception as api_exception: # pylint: disable=W0718
            self.fail(f"Failed to initialize Predictor: {api_exception}")

