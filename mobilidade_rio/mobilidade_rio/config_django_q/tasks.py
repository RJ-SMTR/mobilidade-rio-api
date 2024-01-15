"""Tasks for django-q"""

import logging
from datetime import datetime as dt
import time
from mobilidade_rio.predictor.predictor import Predictor, PredictorFailedException, TPredictorInfo
from mobilidade_rio.predictor.models import PredictorResult


logger = logging.getLogger("cronjob")


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
    existing_results = PredictorResult.objects.filter(  # pylint: disable=E1101
        pk=1)

    if len(existing_results) > 1:
        logger.info(
            "%i PredictorResults duplicados, removendo...",
            len(existing_results))
        existing_results.delete()

    # update db
    logger.info("Salvando no banco de dados...")
    result, created_or_updated = PredictorResult.objects.update_or_create(  # pylint: disable=E1101
        pk=1,
        defaults={
            "result_json": predictor_result
        }
    )

    created_or_updated = "criada" if created_or_updated else "atualizada"
    logger.info(
        "Nova predição %s! total: %d, amostra: %s, retornou erro: %s",
        created_or_updated,
        len(result.result_json['result']),
        result.result_json['result'][:1],
        bool(result.result_json['error'])
    )


def generate_prediction_sleep(wait_secs=30):
    """Runs generate_prediction() multiple times and log elapsed time"""
    start_1 = dt.now()
    logger.info("Iniciando tarefa 1.a - generate_prediction()")
    generate_prediction()

    diff_1 = round((dt.now() - start_1).total_seconds(), 2)
    logger.info("Tarefa de predição 1.a demorou %ss", str(diff_1))

    if diff_1 > 60:
        logger.info("Abortando tarefa 1.b, pois 1.a demorou > 60s")
        return
    if diff_1 < wait_secs:
        time.sleep(wait_secs - diff_1)

    logger.info("Iniciando tarefa 1.b - generate_prediction()")
    start_2 = dt.now()
    generate_prediction()
    diff_2 = round((dt.now() - start_2).total_seconds(), 2)
    diff_total = round((dt.now() - start_1).total_seconds(), 2)
    logger.info("Tarefa 1.b de predição demorou %ss", str(diff_2))
    logger.info("O total das tarefas demorou %ss", str(diff_total))
    logger.info("Tarefa finalizada")
