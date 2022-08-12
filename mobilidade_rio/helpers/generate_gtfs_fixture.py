import json
from typing import List, Union
from pathlib import Path
import re

import pandas as pd
import requests
import yaml


CONFIG_FILENAME = "config_gtfs.yaml"

def load_csv(filepath: Union[str, Path]) -> pd.DataFrame:
    """
    Carrega o arquivo CSV e retorna um DataFrame.
    """
    return pd.read_csv(filepath)

def dump_fixtures(fixtures: List[dict], filepath: Union[str, Path]):
    """
    Salva os fixtures em um arquivo JSON.
    """
    with open(filepath, "w") as f:
        json.dump(fixtures, f, indent=4)

def resolve_e(case,record,i):
    if case == 'route_id[0:1]':
        return record['route_id'][0:1]
    if case == 'mode(1).name(4).tipo(1).versao(1)': #confirmar essa montagem de id - cruzar com o exemplo da planilha.
        return record['route_id'][0:1]+ re.sub('[^0-9]', '', record['route_short_name']).zfill(4) + record['route_id'][-1:]
    if case =='trip_id[-3:]':
        return record['trip_id'][-3:]
    if case =='i':
        return i
    if case == "": #TODO: resolver o caso da via.
        return ""
    if case == "stop_id[4:5]":
        return record["stop_id"][4:5]

def gtfs_to_fixtures(dataframe, config_json, model):
    fixtures = []
    k=config_json["json"]["fields"].keys()
    e=['mode(1).name(4).tipo(1).versao(1)', 'route_id[0:1]','trip_id[-3:]', "i","","stop_id[4:5]"]
    for i, record in dataframe.iterrows():
        result = {
                "model": "pontos."+config_json["json"]["model"],
                "pk": record[config_json["json"]["pk"]] if config_json["json"]["pk"] not in e else resolve_e(config_json["json"]["pk"],record,i),
                "fields": dict.fromkeys(k,"")
            }
        for item in k:
            if config_json["json"]["fields"][item] not in e:
                result["fields"][item]=record[config_json["json"]["fields"][item]]
            else:
                result["fields"][item]=resolve_e(config_json["json"]["fields"][item],record,i)
        fixtures.append(result)

    dump_fixtures(fixtures, f"new_fixtures/{model}.json")

if __name__ == "__main__":
    '''
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
    '''
    
    config = yaml.load(
        open(CONFIG_FILENAME, "r"), 
        Loader=yaml.FullLoader
    )

    for model in config["models"].keys():
        config_json=config["models"][model]
        dataframe = load_csv( config_json['source'] )

        gtfs_to_fixtures(dataframe, config_json, model)