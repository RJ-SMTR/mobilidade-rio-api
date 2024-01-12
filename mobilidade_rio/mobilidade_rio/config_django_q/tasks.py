"""Tasks for django-q"""

import logging
from datetime import datetime as dt
import time
from mobilidade_rio.predictor.predictor import Predictor, PredictorFailedException, TPredictorInfo
from mobilidade_rio.predictor.models import PredictorResult


logger = logging.getLogger("cronjob")


def print_hello():
    """Print to test django-q"""
    print(f"Hello from django-q {dt.now()}")


def generate_prediction():
    """Generate prediction of when buses will arrive at platforms"""
    predictor_error: TPredictorInfo = None
    predictor_eta: list = []

    try:
        pred = Predictor()
        predictor_eta = pred.run_eta()
    except PredictorFailedException as exception:
        predictor_error = exception.info
        exception_message = f'Predictor - {exception.info["code"]}: {exception.info["message"]}'
        if exception.info["type"] == "error":
            logger.error(exception_message)
        if exception.info["type"] == "warning":
            logger.warning(exception_message)
        if exception.info["type"] == "info":
            logger.info(exception_message)

    predictor_result = {
        "result": predictor_eta,
        "error": predictor_error,
    }

    # prevent bug on restoring db while predictor is running
    existing_result = PredictorResult.objects.filter(  # pylint: disable=E1101
        pk=1)

    if len(existing_result) > 1:
        logger.info(
            "%i PredictorResults found, removing duplicates before save...",
            len(existing_result))
        existing_result.delete()

    elif not predictor_result["result"] and predictor_result["error"]:
        logger.info(
            "Predictor returned error only, updating error and keeping the old result")
        predictor_result["result"] = existing_result[0].result_json["result"]

    # update db
    logger.info("saving in db...")
    obj, created_or_updated = PredictorResult.objects.update_or_create(  # pylint: disable=E1101
        pk=1,
        defaults={
            "result_json": predictor_result
        }
    )
    created_or_updated = "created" if created_or_updated else "updated"
    logger.info(
        "New prediction %s! length: %d, preview: %s, has error: %s",
        created_or_updated,
        len(obj.result_json['result']),
        obj.result_json['result'][:1],
        bool(obj.result_json['error'])
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
