"""Camada repository"""

import json
import logging
import os
import re
from typing import Literal, TypedDict
from datetime import datetime as dt

import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account
from typing_extensions import Self


class BigqueryRepositoryInfo(TypedDict):
    """Type for result info, warning or error"""
    code: str
    message: str
    type: Literal["error", "warning", "info"]
    details: dict


class BigqueryRepositoryFailedException(Exception):
    """When failed to run some task"""

    info: BigqueryRepositoryInfo

    def __init__(self, info: BigqueryRepositoryInfo):
        super().__init__(info['message'])
        self.info = info


class BigqueryRepository:
    """Repositório do BigQuery para obter dados de tabelas"""

    _instance = None
    _initialized = False
    client: bigquery.Client = None
    logger = logging.getLogger("BigqueryRepository")

    def __new__(cls) -> Self:
        if not cls._instance:
            cls._instance = super(BigqueryRepository, cls).__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if not self._initialized:
            self.logger = logging.getLogger("BigqueryRepository")
            json_account_info = {
                "type": os.environ.get("GOOGLE_CLIENT_API_TYPE", ""),
                "project_id": os.environ.get("GOOGLE_CLIENT_API_PROJECT_ID", ""),
                "private_key_id": os.environ.get("GOOGLE_CLIENT_API_PRIVATE_KEY_ID", ""),
                #
                "private_key": os.environ.get("GOOGLE_CLIENT_API_PRIVATE_KEY", "").replace("\\n", "\n"),
                "client_email": os.environ.get("GOOGLE_CLIENT_API_CLIENT_EMAIL", ""),
                "client_id": os.environ.get("GOOGLE_CLIENT_API_CLIENT_ID", ""),
                "auth_uri": os.environ.get("GOOGLE_CLIENT_API_AUTH_URI", ""),
                "token_uri": os.environ.get("GOOGLE_CLIENT_API_TOKEN_URI", ""),
                "auth_provider_x509_cert_url": os.environ.get("GOOGLE_CLIENT_API_AUTH_PROVIDER_X509_CERT_URL", ""),
                "client_x509_cert_url": os.environ.get("GOOGLE_CLIENT_API_CLIENT_X509_CERT_URL", ""),
                "universe_domain": os.environ.get("GOOGLE_CLIENT_API_UNIVERSE_DOMAIN", ""),
            }
            """
            private_key:  
                Quando lê do .env ele substirui `\\n` em `\\\\n` e afins: https://github.com/pypa/pipenv/issues/1087
            """

            if not json_account_info["type"]:
                raise BigqueryRepositoryFailedException({
                    "type": "error",
                    "code": "bigquery_repository-error-credentials",
                    "message": "As credenciais não foram carregadas pelo env",
                    "details": json_account_info,
                })

            credentials = service_account.Credentials.from_service_account_info(
                json_account_info)
            self.client = bigquery.Client(credentials=credentials)

            self._initialized = True

    def query(self, query: str) -> pd.DataFrame:
        """Run query"""
        _query = re.sub(r"\n(\s+)(?=\S)", " ", query).replace("\n+", " ")
        self.logger.info("bigquery: %s", _query)
        start = dt.now()

        try:
            rows: pd.DataFrame = self.client.query(query).to_dataframe()
            # Log
            elapsed_time = round((dt.now() - start).total_seconds(), 2)
            self.logger.info("Consulta no Bigquery durou %ss", elapsed_time)

        except Exception as error:  # pylint: disable=W0612
            raise BigqueryRepositoryFailedException({
                "type": "error",
                "code": "bigquery_repository-error-query",
                "message": f"Erro ao realizar a consulta: {error}",
                "details": {},
            }) from error

        return rows
