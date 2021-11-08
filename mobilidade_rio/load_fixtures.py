from sys import argv

import django
from django.db import transaction
from django.core.management import call_command


def load_fixture(name: str):
    with transaction.atomic():
        call_command('loaddata', f'fixtures/{name}.json')


if __name__ == '__main__':
    if len(argv) != 2:
        print('Usage: load_fixtures.py <fixture_name>')
        exit(1)
    django.setup()
    load_fixture(argv[1])
