"""
Copy CSV to Postgres

How to use:

- Put csv files in `csv_files` folder
- Run script 

"""

parameters = """\
--empty_table
"""

import os
import sys
import psycopg2
import json


def upload_data(app, model, flag_params):

    table_name = f"{app}_{model.replace('_', '')}"
    file_path = os.path.join(folder, f"{model}.txt")

    if os.path.isfile(file_path):
        if "empty_table" in flag_params:
            print("Clearing tables...")
            cur.execute(f"TRUNCATE {table_name} CASCADE")
            conn.commit()

        print(f"Inserting data into {table_name}...")
        with open(file_path, "r", encoding="utf8") as f:
            # try:
            # Read null values (string or number)
            cols = f.readline().strip().split(",")
            # cur.copy_from(f, table_name, sep=',', null='', columns=cols)
            cur.copy_expert(
                f"COPY {table_name} ({','.join(cols)}) FROM STDIN DELIMITER ',' CSV;", f
            )
            conn.commit()
            # print(f"Done!")
            # except Exception as e:
            #     conn.rollback()
            # try:
            #     # Read string with comma (ex: "Rio de Janeiro, RJ")
            #     cur.copy_expert(f"COPY {table_name} ({','.join(cols)}) FROM STDIN DELIMITER ',' CSV;", f)
            #     conn.commit()


if __name__ == "__main__":

    if "--help" in sys.argv or "-h" in sys.argv:
        print("Parameters: ")
        print(parameters)
        sys.exit(0)

    # Setting default parameters
    local_path = os.path.dirname(os.path.abspath(__file__))

    csv_path = os.path.join(local_path, "csv_files")
    file_path = os.path.join(local_path, "settings.jsonc")

    try:
        with open(file_path, "r") as f:
            settings = json.load(f)
    except Exception as e:
        raise "Couldn't find settings.jsonc file. Please create one and try again."

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

        if app in settings["django_apps"].keys():
            folder = os.path.join(csv_path, app)
            app_models = settings["django_apps"][app]

            for model in os.listdir(folder):
                model = model.split(".")[0]

                if model in app_models:
                    print(f"Uploading {model} data...")
                    upload_data(app, model, flag_params)
                    print(f"Done uploading {model} data.")
        else:
            print(
                f"Couldn't find {app} in settings.jsonc. Make sure you have the correct app name - should be a folder in mobilidade_rio/mobilidade_rio."
            )
