"""
Copy CSV to Postgres

How to use:

- Put csv files in `csv_files` folder

- Run script 

"""

parameters = \
"""\
--host
--port
--user
--password
--database
--csv_path
--table_prefix
--header
"""

import os
import sys
import psycopg2

# print help if --help or -h

if '--help' in sys.argv or '-h' in sys.argv:
    print("parameters:")
    print(parameters)
    sys.exit(0)

# Current script path

local_path = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(local_path, "csv_files")


# Settings

db_params = {
    'host ': 'localhost',
    'port': '5432',
    'user': 'postgres',
    'password': 'postgres',
    'database': 'postgres',
}

table_order = [
    'agency',
    'route',
    'trip',
    'stop',
    'qr_code'
    # 'stop_times',
]

script_params = {
    'csv_path': csv_path,
    'table_prefix': 'pontos_',
    'table_order': ",".join(table_order),  # agency,route,trip,etc
}

flag_params = [
    'empty_table',
    'no_insert',
]


# Pass parameters

for key in db_params.keys():
    # --host localhost
    for i, arg in enumerate(sys.argv):
        if arg == f"--{key}":
            db_params[key] = sys.argv[i+1]

for key in script_params.keys():
    # --csv_path /home/user/csv_files
    for i, arg in enumerate(sys.argv):
        if arg == f"--{key}":
            script_params[key] = sys.argv[i+1]

# Remove flag params if not in sys.argv (--param)
flag_params = [param for param in flag_params if f"--{param}" in sys.argv]

# Convert back to list

table_order = script_params['table_order'].split(',')

# Utils

def get_table_name(name):
    if script_params['table_prefix']:
        return f"{script_params['table_prefix']}{name}"
    return name

def treat_data(data_str, table_name):
    # get first line
    first = data_str.split()

def get_db_cols(table_name, cursor):
    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
    return [col[0] for col in cursor.fetchall()]

# Conect to the database

conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Add files with native postgre's COPY command

file_list = os.listdir(script_params['csv_path'])

# Order files
_table_order = table_order.copy()
for i, table_names in enumerate(table_order):
    if table_names+'.csv' not in file_list:
        _table_order.remove(table_names)
file_list = _table_order


# Copy files

# Clear tables if --empty_table
if 'empty_table' in flag_params:
    print("Clearing tables")
    for table_name in file_list:
        cur.execute(f"TRUNCATE {get_table_name(table_name)} CASCADE")
        conn.commit()

for table_name in file_list:
    file_name = f"{table_name}.csv"
    table_name = get_table_name(table_name)
    file_path = os.path.join(script_params['csv_path'], file_name)

    print(f"Copying {file_path} to {table_name}")
    if 'no_insert' not in flag_params:
        with open(file_path, 'r', encoding="utf8") as f:
            cols = f.readline().strip().split(',')

            try:
                # Read null values (string or number)
                cur.copy_from(f, table_name, sep=',', null='', columns=cols)
                conn.commit()
            except Exception as e:
                conn.rollback()
                try:
                    # Read string with comma (ex: "Rio de Janeiro, RJ")
                    cur.copy_expert(f"COPY {table_name} ({','.join(cols)}) FROM STDIN DELIMITER ',' CSV;", f)
                    conn.commit()
                except Exception as e:
                    print("csv collumns:\n",cols)
                    conn.rollback()
                    db_cols = get_db_cols(table_name, cur)
                    print("db collumns:\n", db_cols)
                    exit(1)
            