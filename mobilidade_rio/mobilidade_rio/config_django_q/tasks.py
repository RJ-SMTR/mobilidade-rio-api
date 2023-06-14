"""Tasks for django-q"""

import logging
from datetime import datetime as dt
import time
from mobilidade_rio.predictor.utils import Predictor
from mobilidade_rio.predictor.models import PredictorResult


logger = logging.getLogger("cronjob")


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
    logger.info("saving in db...")

    # prevent bug on restoring db while predictor is running
    duplicated_pk = PredictorResult.objects.filter(pk=1)
    if len(duplicated_pk) > 1:
        logger.info("%i PredictorResults found, removing duplicates before save...", len(duplicated_pk))
        duplicated_pk.delete()

    obj, created_or_updated = PredictorResult.objects.update_or_create(
        pk=1,
        defaults={
            "result_json": predictor_result
        }
    )
    created_or_updated = "created" if created_or_updated else "updated"
    logger.info(
        "new prediction %s! length: %d, preview: %s",
        created_or_updated,
        len(obj.result_json['result']),
        obj.result_json['result'][:1]
        )


# TODO: Decide if this function will recall itself every 20 seconds 3x or if apps.py will do it.
def generate_prediction_sleep(wait_secs=30):
    start_1 = dt.now()
    logger.info("Starting job 1.a - generating prediction")
    generate_prediction()

    diff_1 = round((dt.now() - start_1).total_seconds(), 2)
    logger.info("Job 1.a prediction took %ss", str(diff_1))

    if diff_1 > 60:
        logger.info("Aborting job 1.b, 1.a took > 60s")
        return
    if diff_1 < wait_secs:
        time.sleep(wait_secs - diff_1)

    logger.info("Starting job 1.b - generating prediction")
    start_2 = dt.now()
    generate_prediction()
    diff_2 = round((dt.now() - start_2).total_seconds(), 2)
    diff_total = round((dt.now() - start_1).total_seconds(), 2)
    logger.info("Job 1.b prediction took %ss", str(diff_2))
    logger.info("Jobs total prediction took %ss", str(diff_total))
    logger.info("finished job")
