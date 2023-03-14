"""Tasks for django-q"""

from datetime import datetime as dt, timedelta
import pandas as pd
import time
from mobilidade_rio.predictor.utils import Predictor
from mobilidade_rio.predictor.models import PredictorResult


def print_hello():
    """Print to test django-q"""
    print(f"Hello from django-q {dt.now()}")


def generate_prediction():
    pred = Predictor()
    predictor_result = {"result": pred.run_eta()}
    PredictorResult.objects.filter(pk=1).delete()
    PredictorResult.objects.create(pk=1, result_json=predictor_result)


# TODO: Decide if this function will recall itself every 20 seconds 3x or if apps.py will do it.
def generate_prediction_sleep(wait_secs=30):
    print("generate_prediction_sleep v1")
    start = dt.now()
    generate_prediction()
    diff = (dt.now() - start).total_seconds()
    print("Prediction's time taken:", diff)
    if diff < wait_secs:
        time.sleep(wait_secs - diff)
    generate_prediction()
