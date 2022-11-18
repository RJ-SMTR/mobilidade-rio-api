"""
Copy CSV to Postgres

How to use:

- Put csv files in `csv_files` folder
- Run script

"""

import json
import sys
import os
import psycopg2

PARAMETERS = """\
--empty_table
--no_dada
"""


def upload_data(_app: str, _model: str, _flag_params: str):
    """
    Upload data to Postgres

    Args:
        app (str): app name
        model (str): model name
        flag_params (str): flag parameters

    Returns:
        None
    """

    table_name = f"{_app}_{_model.replace('_', '')}"
    file_path_1 = os.path.join(folder, f"{_model}.txt")

    if os.path.isfile(file_path_1):
        
        if "--no_insert" not in sys.argv:
            print(f"Table '{table_name}'  - ", end='')
            with open(file_path_1, 'r', encoding="utf8") as f_1:
                cols = f_1.readline().strip().split(',')

                # clear table
                if "empty_table" in _flag_params:
                    print("clearing ", end='')
                    cur.execute(f"TRUNCATE {table_name} CASCADE")
                    conn.commit()
                # Read null values (string or number)
                print("inserting ", end='')
                cur.copy_expert(f"COPY {table_name} ({','.join(cols)}) \
                                    FROM STDIN DELIMITER ',' CSV;", f_1)
                conn.commit()
    print("[OK]")


if __name__ == "__main__":

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Parameters: ")
        print(PARAMETERS)
        sys.exit(0)

    # Setting default parameters
    local_path = os.path.dirname(os.path.abspath(__file__))

    csv_path = os.path.join(local_path, "csv_files")
    file_path = os.path.join(local_path, "settings.json")

    try:
        with open(file_path, "r", encoding="utf8") as f:
            settings = json.load(f)
    finally:
        # raise string
        print("Couldn't find settings.json file. Please create one and try again.")

    for key in settings["db_params"].keys():
        for i, arg in enumerate(sys.argv):
            if arg == f"--{key}":
                settings["db_params"][key] = sys.argv[i + 1]

    # Remove flag params if not in sys.argv (--param)
    flag_params = [
        param for param in settings["flag_params"] if f"--{param}" in sys.argv
    ]

    # Connect to the database
    print("\nConnecting to the PostgreSQL database...")
    conn = psycopg2.connect(**settings["db_params"])
    cur = conn.cursor()

    # Update data from files in csv_path
    for app in os.listdir(csv_path):

        if app in settings["table_order"].keys():
            folder = os.path.join(csv_path, app)
            app_models = settings["table_order"][app]

            for model in os.listdir(folder):
                model = model.split(".")[0]

                if model in app_models:
                    upload_data(app, model, flag_params)
        else:
            print(
                f"Couldn't find {app} in 'settings.json'.\n\
                Make sure you have the correct app name - \
                should be a folder in mobilidade_rio/mobilidade_rio."
            )
