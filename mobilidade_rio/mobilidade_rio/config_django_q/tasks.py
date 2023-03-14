"""Tasks for django-q"""

from datetime import datetime as dt, timedelta
import pandas as pd
import time
from mobilidade_rio.predictor.utils import Predictor
from mobilidade_rio.predictor.models import PredictorResult
import logging

logger = logging.getLogger("[tasks]")


def print_hello():
    """Print to test django-q"""
    print(f"Hello from django-q {dt.now()}")


def generate_prediction():
    pred = Predictor()
    predictor_result = pred.run_eta()
    predictor_result = {"result": predictor_result}
    logger.debug("saving in db")
    obj, created = PredictorResult.objects.update_or_create(
        pk=1,
        defaults={
            "result_json": predictor_result
        }
    )
    logger.debug(f"obj new content: {obj.result_json['result'][0]}")
    # logger.debug(f"obj created or updated? {created}")


# TODO: Decide if this function will recall itself every 20 seconds 3x or if apps.py will do it.
def generate_prediction_sleep(wait_secs=30):
    start = dt.now()
    logger.info("starting job 1 - generating prediction")
    generate_prediction()
    
    diff = (dt.now() - start).total_seconds()
    if diff < wait_secs:
        time.sleep(wait_secs - diff)

    logger.info(f"starting job 1.b - generating prediction - last prediction took {diff}s")
    generate_prediction()
    logger.info(f"finished job")