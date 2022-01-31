import json
import random
from typing import List
import requests
import os
import yaml

from dotenv import load_dotenv
load_dotenv()

DEFAULT_TIMEOUT = 60
CONFIG_FILENAME = "helpers/config.yaml"
ACTIVE_FILENAME = "helpers/trip_id_regular.json"
STOP_FIXTURE_FILENAME = "fixtures/stop.json"
OUTPUT_JSON = f"fixtures/{{model}}.json"

###
# Utils
###

active = json.load(open(ACTIVE_FILENAME, "r"))
# TODO: create rule for active trips based on gps
def _is_active(record: dict, model: str) -> None:
    """
    Check if id is active. Currently includes:
    
    * trip
    * route
    * linha
    * sequence
    """
    if model == "sequence": 
        model = "trip"
        id = record["fields"]["trip"]
    else:
        id = record["pk"]

    if model in ["trip", "route", "linha"]:
        if id not in active[f"{model}_id"]:
            print(f"ID not active for {model}: {id}")
            return False
    return True


def _fetch_sigmob_api(url: str) -> List[dict]:
    """
    Fetches SIGMOB endpoints, whether they have pagination or not.
    """
    results: list = []
    next: str = url
    while next:
        try:
            print("Fetching %s" % next)
            data = requests.get(next, timeout=DEFAULT_TIMEOUT)
            data.raise_for_status()
            data = data.json()
            if "result" in data:
                results.extend(data["result"])
            elif "data" in data:
                results.extend(data["data"])
            if "next" in data and data["next"] != "EOF" and data["next"] != "":
                next = data["next"]
            else:
                next = None
        except Exception as e:
            raise e
    return results


def _parse_data_to_fixture(data: dict, config: dict, i: int) -> dict:
    _fix_null = lambda x: x if x else ""

    result = {
        "model": "pontos."+config["model"],
        "pk": data[config["pk"]] if config["pk"] else i,
        "fields": dict()
        # "fields": {k: _fix_null(data[v]) for k,v in config["fields"].items()}
    }
    # TODO: fix bug on max_lenght field
    for k,v in config["fields"].items():
        if "fix_lenght" in config:
            if k in config["fix_lenght"]:
                data[v] = data[v][:config["fix_lenght"][k]]
        result["fields"][k] = _fix_null(data[v])
    return result


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Gera fixtures de a partir do SIGMOB."
    )
    parser.add_argument(
        "--model", "-m",
        type=str,
        help="Modelo de fixture a ser gerado."
    )
    parser.add_argument(
        "--upload", "-u",
        action=argparse.BooleanOptionalAction,
        type=bool,
        help="Indica se deseja subir os dados no cluster k8s."
    )
    args = parser.parse_args()
    model = args.model
    upload = args.upload

    config = yaml.load(
        open(CONFIG_FILENAME, "r"), 
        Loader=yaml.FullLoader
    )["models"][model]

    result = _fetch_sigmob_api(config["source"])

    fixture = []
    for i, record in enumerate(result):
        record = _parse_data_to_fixture(record, config["json"], i)
        if _is_active(record, model):
            fixture.append(record)
    
    fname = OUTPUT_JSON.format(model=model)
    with open(fname, "w", encoding='utf8') as f:
        json.dump(fixture, f, indent=4, ensure_ascii=False)
        print("Fixture saved on "+fname)
    if upload:
        os.system(f"kubectl cp {fname} mobilidade-v2/{os.getenv('K8S_POD')}:/app/{fname}")
        print("Uploaded to production db")

