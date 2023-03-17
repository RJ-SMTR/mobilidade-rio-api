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
    try:
        pred = Predictor()
    except Exception as api_exception:
        logger.error(f"Predictor - {api_exception}")
        return
    predictor_result = pred.run_eta()
    predictor_result = {"result": predictor_result}
    logger.info("saving in db")
    obj, created = PredictorResult.objects.update_or_create(
        pk=1,
        defaults={
            "result_json": predictor_result
        }
    )
    logger.info(f"obj new content: {obj.result_json['result'][0]}")
    # logger.info(f"obj created or updated? {created}")


# TODO: Decide if this function will recall itself every 20 seconds 3x or if apps.py will do it.
def generate_prediction_sleep(wait_secs=30):
    start_1 = dt.now()
    logger.info("starting job 1.a - generating prediction")
    generate_prediction()

    diff_1 = round((dt.now() - start_1).total_seconds(), 2)
    logger.info(f"Job 1.a prediction took {diff_1}s")

    if diff_1 > 60:
        logger.info("Aborting job 1.b, 1.a took > 60s")
        return
    if diff_1 < wait_secs:
        time.sleep(wait_secs - diff_1)

    logger.info("starting job 1.b - generating prediction")
    start_2 = dt.now()
    generate_prediction()
    diff_2 = round((dt.now() - start_2).total_seconds(), 2)
    diff_total = round((dt.now() - start_1).total_seconds(), 2)
    logger.info(f"Job 1.b prediction took {diff_2}s")
    logger.info(f"Jobs total prediction took {diff_total}s")
    logger.info("finished job")
