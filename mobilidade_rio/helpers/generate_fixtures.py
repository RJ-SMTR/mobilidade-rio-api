import json
import random
from typing import List
import requests

import pandas as pd

DEFAULT_TIMEOUT = 60
SIGMOB_AGENCY_URL = "http://jeap.rio.rj.gov.br/MOB/get_agency.rule?sys=MOB"
SIGMOB_LINHAS_URL = "http://jeap.rio.rj.gov.br/MOB/get_linhas.rule?sys=MOB"
SIGMOB_ROUTES_URL = "http://jeap.rio.rj.gov.br/MOB/get_routes.rule?sys=MOB"
SIGMOB_STOPS_URL = "http://jeap.rio.rj.gov.br/MOB/get_stops.rule?sys=MOB&INDICE=0"
SIGMOB_TRIPS_URL = "http://jeap.rio.rj.gov.br/MOB/get_trips.rule?sys=MOB"
STOP_FIXTURE_FILENAME = "fixtures/stop.json"
SIGMOB_SEQUENCE_URL = "http://jeap.rio.rj.gov.br/MOB/get_stop_times.rule?sys=MOB"

###
# Utils
###


def fetch_sigmob_api(url: str) -> List[dict]:
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


###
# Agency
###


def parse_sigmob_agency_to_fixture_json(agency: dict):
    return {
        "model": "pontos.agency",
        "pk": agency["agency_id"],
        "fields": {
            "name": agency["agency_name"],
        }
    }


def generate_fixtures_for_agency(fname: str) -> None:
    agencies = fetch_sigmob_api(SIGMOB_AGENCY_URL)
    fixture = [parse_sigmob_agency_to_fixture_json(
        agency) for agency in agencies]
    with open(fname, "w") as f:
        json.dump(fixture, f, indent=4)

###
# Linha
###


def parse_sigmob_linha_to_fixture_json(linha: dict):
    return {
        "model": "pontos.linha",
        "pk": linha["linha_id"],
        "fields": {
            "agency": linha["agency_id"],
            "mode": linha["idModalSmtr"],
            "initials": linha["sigla"],
            "name": linha["NomeLinha"]
        }
    }


def generate_fixtures_for_linha(fname: str) -> None:
    linhas = fetch_sigmob_api(SIGMOB_LINHAS_URL)
    fixture = [parse_sigmob_linha_to_fixture_json(
        linha) for linha in linhas]
    with open(fname, "w") as f:
        json.dump(fixture, f, indent=4)

###
# Route
###


def parse_sigmob_route_to_fixture_json(route: dict):
    return {
        "model": "pontos.route",
        "pk": route["route_id"],
        "fields": {
            "linha": route["linha_id"],
            "agency": route["agency_id"],
            "mode": route["idModalSmtr"],
            "short_name": route["route_short_name"],
            "vista": route["Vista"]
        }
    }


def generate_fixtures_for_route(fname: str) -> None:
    routes = fetch_sigmob_api(SIGMOB_ROUTES_URL)
    fixture = [parse_sigmob_route_to_fixture_json(
        route) for route in routes]
    with open(fname, "w") as f:
        json.dump(fixture, f, indent=4)


###
# Trip
###

def parse_sigmob_trip_to_fixture_json(trip: dict):
    return {
        "model": "pontos.trip",
        "pk": trip["trip_id"],
        "fields": {
            "route": trip["route_id"],
            "headsign": trip["trip_headsign"],
            "via": trip["via"],
            "version": trip["versao"],
            "direction": trip["Direcao"],
        }
    }


def generate_fixtures_for_trip(fname: str) -> None:
    trips = fetch_sigmob_api(SIGMOB_TRIPS_URL)
    fixture = [parse_sigmob_trip_to_fixture_json(
        trip) for trip in trips]
    with open(fname, "w") as f:
        json.dump(fixture, f, indent=4)

###
# Stop
###


def parse_sigmob_stop_to_fixture_json(stop: dict):
    return {
        "model": "pontos.stop",
        "pk": stop["stop_id"],
        "fields": {
            "mode": stop["idModalSmtr"],
            "name": stop["stop_name"],
            "address": stop["endereco"],
            "latitude": stop["stop_lat"],
            "longitude": stop["stop_lon"],
        }
    }


def generate_fixtures_for_stop(fname: str) -> None:
    stops = fetch_sigmob_api(SIGMOB_STOPS_URL)
    fixture = [parse_sigmob_stop_to_fixture_json(
        stop) for stop in stops]
    with open(fname, "w") as f:
        json.dump(fixture, f, indent=4)

###
# Sequence
###


def parse_sigmob_sequence_to_fixture_json(sequence: dict, i: int):
    return {
        "model": "pontos.sequence",
        "pk": i,
        "fields": {
            "trip": sequence["trip_id"],
            "stop": sequence["stop_id"],
            "order": sequence["stop_sequence"],
        }
    }


def generate_fixtures_for_sequence(fname: str) -> None:
    sequences = fetch_sigmob_api(SIGMOB_SEQUENCE_URL)
    fixture = [parse_sigmob_sequence_to_fixture_json(
        sequence, i) for i, sequence in enumerate(sequences)]
    with open(fname, "w") as f:
        json.dump(fixture, f, indent=4)


###
# QrCode
###

def generate_random_qrcode() -> str:
    allowed_chars = "ABCDEFGHJKLMNPQRSTUVWXYZ0123456789"
    return "".join(random.choice(allowed_chars) for _ in range(4))


def parse_stop_to_qrcode_fixture_json(stop: dict, i: int):
    return {
        "model": "pontos.qrcode",
        "pk": i,
        "fields": {
            "stop": stop["pk"],
            "code": generate_random_qrcode(),
        }
    }


def generate_fixtures_for_qrcode(fname: str) -> None:
    with open(STOP_FIXTURE_FILENAME, "r") as f:
        stops = json.load(f)
    fixture = [parse_stop_to_qrcode_fixture_json(
        stop, i) for i, stop in enumerate(stops)]
    with open(fname, "w") as f:
        json.dump(fixture, f, indent=4)
