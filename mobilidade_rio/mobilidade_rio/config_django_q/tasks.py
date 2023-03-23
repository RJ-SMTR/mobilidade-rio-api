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
        logger.info("Predictor - %s", api_exception)
        return
    predictor_result = pred.run_eta()
    predictor_result = {"result": predictor_result}
    logger.info("%s saving in db", dt.now().time())
    # obj, created?
    obj, _ = PredictorResult.objects.update_or_create(
        pk=1,
        defaults={
            "result_json": predictor_result
        }
    )
    logger.info("obj new content: %s", obj.result_json['result'][:1])


# TODO: Decide if this function will recall itself every 20 seconds 3x or if apps.py will do it.
def generate_prediction_sleep(wait_secs=30):
    start_1 = dt.now()
    logger.info("%s Starting job 1.a - generating prediction", dt.now().time())
    generate_prediction()

    diff_1 = round((dt.now() - start_1).total_seconds(), 2)
    logger.info("%s Job 1.a prediction took %ss", dt.now().time(), str(diff_1))

    if diff_1 > 60:
        logger.info("%s Aborting job 1.b, 1.a took > 60s", dt.now().time())
        return
    if diff_1 < wait_secs:
        time.sleep(wait_secs - diff_1)

    logger.info("%s Starting job 1.b - generating prediction", dt.now().time())
    start_2 = dt.now()
    generate_prediction()
    diff_2 = round((dt.now() - start_2).total_seconds(), 2)
    diff_total = round((dt.now() - start_1).total_seconds(), 2)
    logger.info("%s Job 1.b prediction took %ss", dt.now().time(), str(diff_2))
    logger.info("%s Jobs total prediction took %ss", dt.now().time(), str(diff_total))
    logger.info("%s finished job", dt.now().time())
