"""
Código para gerar os fixtures de QRCode através de um arquivo CSV.

    - O arquivo CSV deve ter o seguinte formato:
        - Cabeçalho:
            - code - Código do QRCode
            - stop - Código da parada de acordo com o sigmob

    - A saída do código é um arquivo JSON com os dados do QRCode.
    Ele terá o seguinte formato:
        [
            {
                "model": "pontos.qrcode",
                "pk": <id no banco de dados>,
                "fields": {
                    "stop": <id da parada>,
                    "code": <código do QRCode>,
                }
            },
            ...
        ]
"""

import json
from typing import List, Union
from pathlib import Path

import pandas as pd
import requests

QRCODE_URL = "https://api.mobilidade.rio/qrcode/"


def load_csv(filepath: Union[str, Path]) -> pd.DataFrame:
    """
    Carrega o arquivo CSV e retorna um DataFrame.
    """
    return pd.read_csv(filepath)


def convert_to_fixtures(dataframe: pd.DataFrame, start_id: int = 0) -> List[dict]:
    """
    Converte o DataFrame para um dicionário de fixtures.
    """
    fixtures = []
    for index, row in dataframe.iterrows():
        fixtures.append({
            "model": "pontos.qrcode",
            "pk": index + start_id,
            "fields": {
                "stop": row["stop"],
                "code": row["code"],
            }
        })
    return fixtures


def dump_fixtures(fixtures: List[dict], filepath: Union[str, Path]):
    """
    Salva os fixtures em um arquivo JSON.
    """
    with open(filepath, "w") as f:
        json.dump(fixtures, f, indent=4)


def get_default_start_id() -> int:
    """
    Retorna o id inicial padrão para os fixtures.
    """
    request = requests.get(QRCODE_URL)
    data = request.json()
    return data["count"]


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Gera fixtures de QRCode a partir de um arquivo CSV."
    )
    parser.add_argument(
        "csv_file",
        type=str,
        help="Arquivo CSV com os dados dos QRCodes."
    )
    parser.add_argument(
        "output_file",
        type=str,
        help="Arquivo JSON com os dados dos QRCodes."
    )
    parser.add_argument(
        "--start-id",
        type=int,
        help="ID inicial dos fixtures.",
        required=False,
        default=get_default_start_id(),
    )
    args = parser.parse_args()

    csv_file = Path(args.csv_file)
    output_file = Path(args.output_file)
    start_id = args.start_id

    dataframe = load_csv(csv_file)
    fixtures = convert_to_fixtures(dataframe, start_id)
    dump_fixtures(fixtures, output_file)
