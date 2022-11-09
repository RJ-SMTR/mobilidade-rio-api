"""
Copy CSV to Postgres

How to use:

- Put csv files in `csv_files` folder

- Run script 

Parameters (optional):
    --host
    --port
    --user
    --password
    --database

    --table_prefix
    --csv_path
    --header
"""

import os
import sys
import psycopg2

# Current script path

local_path = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(local_path, "csv_files")


# Settings

db_params = {
    'host': 'localhost',
    'port': '5432',
    'user': 'postgres',
    'password': 'postgres',
    'database': 'postgres',
}

script_params = {
    'csv_path': csv_path,
    'table_prefix': 'pontos_',
    'empty_table': 'false',
}


# Utils

def get_table_name(name):
    if script_params['table_prefix']:
        return f"{script_params['table_prefix']}{name}"
    return name


# Pass parameters

for key in db_params.keys():
    for arg in sys.argv:
        if arg.startswith('--' + key + '='):
            db_params[key] = arg.split('=')[1]

for key in script_params.keys():
    for arg in sys.argv:
        if arg.startswith('--' + key + '='):
            script_params[key] = arg.split('=')[1]


# Conect to the database

conn = psycopg2.connect(**db_params)
cur = conn.cursor()

# Add files with native postgre's COPY command

for file in os.listdir(script_params['csv_path']):
    if file.endswith('.csv'):
        # remove all elements from table, but not the table itself
        if script_params['empty_table'] == 'true':
            cur.execute(f"TRUNCATE TABLE {get_table_name(file.split('.')[0])};")
            conn.commit()

        with open(os.path.join(script_params['csv_path'], file), 'r') as f:
            # copy and use the first line as header, without variable script_params['header']
            copy_sql = f"""
                COPY {get_table_name(file.replace('.csv', ''))}
                FROM STDIN
                CSV HEADER
                DELIMITER AS ','
                ;"""
            
            cur.copy_expert(copy_sql, f)
            conn.commit()

            # # 
            # next(f)  # Skip the header row.
            # cur.copy_from(f, get_table_name(
            #     file.split('.')[0]),
            #     sep=',',
            # )