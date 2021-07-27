import json
import random
import requests

import pandas as pd

SIGMOB_AGENCY_URL = "http://jeap.rio.rj.gov.br/MOB/get_agency.rule?sys=MOB"
SIGMOB_LINHAS_URL = "http://jeap.rio.rj.gov.br/MOB/get_linhas.rule?sys=MOB"
SIGMOB_ROUTES_URL = "http://jeap.rio.rj.gov.br/MOB/get_routes.rule?sys=MOB"
SIGMOB_TRIPS_URL = "http://jeap.rio.rj.gov.br/MOB/get_trips.rule?sys=MOB"
SIGMOB_STOP_FILENAME = "helpers/stops.csv"
STOP_FIXTURE_FILENAME = "fixtures/stop.json"
SIGMOB_SEQUENCE_URL = "http://jeap.rio.rj.gov.br/MOB/get_stop_times.rule?sys=MOB"

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
    response = requests.get(SIGMOB_AGENCY_URL)
    agencies = response.json()["result"]
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
    response = requests.get(SIGMOB_LINHAS_URL)
    linhas = response.json()["result"]
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
    response = requests.get(SIGMOB_ROUTES_URL)
    routes = response.json()["result"]
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
    response = requests.get(SIGMOB_TRIPS_URL)
    trips = response.json()["result"]
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
    df = pd.read_csv(SIGMOB_STOP_FILENAME)
    fixture = []
    for _, stop in df.iterrows():
        fixture.append(parse_sigmob_stop_to_fixture_json(stop))
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
    response = requests.get(SIGMOB_SEQUENCE_URL)
    sequences = response.json()["result"]
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
