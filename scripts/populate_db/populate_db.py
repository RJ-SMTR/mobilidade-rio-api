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
import json


# Utils

def json5_loads(js_content):
    # replace "return "
    js_content = js_content.replace("return ", "")
    # remove whole line if starts with "//"
    js_content = "".join([line for line in js_content.splitlines(True) if not line.strip().startswith("//")])
    # remove last comma if next line is "}" or "]"
    js_content = js_content.replace(",\n}", "\n}").replace(",\n]", "\n]")
    
    loop = True
    while loop:
        try:
            conf_json = json.loads(js_content)
            loop = False
        except json.decoder.JSONDecodeError as e:
            # if error is "Expecting value", remove last comma from value
            if e.msg == "Expecting value":
                js_content = js_content.splitlines()
                line_index = e.lineno - 1
                line = js_content[line_index]
                # if line ends with ] or }, go to previous line
                if [line.endswith(s) for s in (["}", "]", "},", "],"])]:
                    line_index -= 1
                    line = js_content[line_index]
                # remove last comma
                line = line[:line.rfind(",")]
                js_content[line_index] = line
                js_content = "\n".join(js_content)
            else:
                raise
    return conf_json

def get_db_cols(table_name, cursor):
    cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name = '{table_name}'")
    return [col[0] for col in cursor.fetchall()]


# Variables

local_path = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(local_path, "csv_files")


# Default settings

db_params = {
    'host ': 'localhost',
    'port': '5432',
    'user': 'postgres',
    'password': 'postgres',
    'database': 'postgres',
}

table_order = {
    'pontos': [
        'agency',
        'route',
        'trip',
        'stop',
        'qrcode',
        'stop_tst',
    ],
    'folder2': [
        'table1',
    ]
}

script_params = {
    'csv_path': csv_path,
}

flag_params = [
    'empty_table',
    'no_insert',
]

# Convert back to list
# table_order = script_params['table_order'].split(',')

# if file exists
file_path = os.path.join(local_path, "settings.jsonc")
if os.path.isfile(file_path):
    with open(file_path, 'r') as f:
        settings = json5_loads(f.read())
    # Update settings
    db_params.update(settings.get('db_params', {}))
    table_order.update(settings.get('table_order', {}))
else:
    print("No settings.jsonc file found, using default settings.")

# Parameters

# print help if --help or -h

if '--help' in sys.argv or '-h' in sys.argv:
    print("parameters:")
    print(parameters)
    sys.exit(0)

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



# App start

# Conect to the database
conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Filter and order files per folder

# get folders if in table_order
file_folders = os.listdir(script_params['csv_path'])
file_folders = [folder for folder in file_folders if folder in table_order]

_table_order = table_order.copy()

# Remove keys if not in file_folders
_table_order = {key: _table_order[key] for key in _table_order if key in file_folders}

# Remove values if not in file_folders
for key in _table_order:
    file_list = os.listdir(os.path.join(script_params['csv_path'], key))
    _table_order[key] = [value for value in _table_order[key] if value+".csv" in file_list]
table_order = _table_order


# Loop through folders

for folder, tables in table_order.items():

    # Copy files

    # Clear tables if --empty_table
    if 'empty_table' in flag_params:
        print("Clearing tables")
        for table_name in tables:
            table_name = f"{folder}_{table_name}"
            cur.execute(f"TRUNCATE {table_name} CASCADE")
            conn.commit()

    # Insert table if not --no_insert
    if 'no_insert' not in flag_params:
        for table_name in tables:
            file_name = f"{table_name}.csv"
            table_name = f"{folder}_{table_name}"
            # file path = csv_path/folder/file_name
            file_path = os.path.join(script_params['csv_path'], folder, file_name)

            print(f"Copying {file_path} to {table_name}")
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