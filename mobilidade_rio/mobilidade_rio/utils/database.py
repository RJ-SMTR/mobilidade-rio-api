"""database utils"""
from time import sleep
from django.db import OperationalError, connections


def check_database_connection(max_retry: int = None, retry_secs: float = 1):
    """
    Safe check Django connection with database

    retry_secs:
        Django takes 3s to establish connection, so if value is 1s, the system will take 1s + 3s
    """
    retry = 0
    while max_retry is None or retry < max_retry:
        try:
            connection = connections['default']
            connection.ensure_connection()
            return
        except OperationalError as e:
            if max_retry is None or retry < max_retry:
                if max_retry is not None and retry < max_retry:
                    retry += 1
                print(f"\nDatabase connection failed: {e}",
                      f"Retrying in {retry_secs} seconds...")
                sleep(retry_secs)
                continue
