import json

TRIPS_FILE = "fixtures/trip.json"
SEQUENCES_FILE = "fixtures/sequence.json"

with open(SEQUENCES_FILE, "r") as f:
    sequences = json.load(f)

with open(TRIPS_FILE, "r") as f:
    trips = json.load(f)

trip_ids = set([trip["pk"] for trip in trips])
sequence_trip_ids = set([sequence["fields"]["trip"] for sequence in sequences])

for t in (sequence_trip_ids - trip_ids):
    print(f"Sequence with trip {t} not found")
