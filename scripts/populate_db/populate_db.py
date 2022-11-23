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
import pandas

PARAMETERS = """\
--exclude_tables
--no_dada
-p --port
"""

remove_duplicates_col = {
    "pontos_stop_times": {
        "trip_id"
    },
    "pontos_trips": {
        "trip_id"
    }
}


def filter_col(data, table: str, cols: list) -> str:
    """
    Filter columns before upload

    Args:
        data (str): data input

    Returns:
        filtered data (str): filtered data output
    """

    # if table name in key
    if table in remove_duplicates_col:
        for col in remove_duplicates_col[table]:
            if col in cols:
                dataframe = pandas.read_csv(data, sep=",", encoding="utf8", low_memory=False)
                dataframe[col]= dataframe[col].str.split("_").str[0]
                dataframe = dataframe.drop_duplicates(subset=[col])
                print("FILTERING...")

                # save log csv file
                dataframe.to_csv(os.path.join(folder, "temp.csv"), index=False, header=False)

                # save to postgres (exclude header)
                return open(os.path.join(folder, "temp.csv"), 'r', encoding="utf8")
    return data


def clear_table(_app: str, _model: str, suffix: str = ""):
    """
    Clear tables

    Args:
        app (str): app name
        model (str): model name
        flag_params (str): flag parameters

    Returns:
        None
    """

    table_name = f"{_app}_{_model.replace('_', '')}"
    if suffix:
        table_name = f"{table_name}_{suffix}"
    if "--exclude_tables" in sys.argv:
        cur.execute(f"TRUNCATE {table_name} CASCADE")
        conn.commit()

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
    print(_model)
    
    if os.path.isfile(file_path_1):
        print(f"Table '{table_name}'")
        with open(file_path_1, 'r', encoding="utf8") as f_1:
            # Insert data
            if "--no_insert" not in sys.argv:
                # Filter table
                cols = f_1.readline().strip().split(',')
                f_1.seek(0)
                print("Filtering...")
                data = filter_col(f_1, table_name, cols)
                # Insert table
                print("inserting ...")
                # copy with loading bar
                cur.copy_expert(f"COPY {table_name} ({','.join(cols)}) \
                                    FROM STDIN DELIMITER ',' CSV;", data)
                conn.commit()
    print("[OK]\n")


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
    db_params = settings["db_params"]

    # if -p or --port in sys.argv:
    db_params["port"] = sys.argv[sys.argv.index("-p") + 1] \
        if "-p" in sys.argv else db_params["port"]
    db_params["port"] = sys.argv[sys.argv.index("--port") + 1] \
        if "--port" in sys.argv else db_params["port"]

    # Remove flag params if not in sys.argv (--param)
    flag_params = [
        param for param in settings["flag_params"] if f"--{param}" in sys.argv
    ]

    # Connect to the database
    print("\nConnecting to the PostgreSQL database...")
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # Update data from files in csv_path
    for app in os.listdir(csv_path):

        # Clear all tables
        if "--exclude_tables" in sys.argv:
            print(f"Clearing all tables in {app}:")
            if app in settings["table_order"].keys():
                folder = os.path.join(csv_path, app)
                app_models = settings["table_order"][app]
                for model in os.listdir(folder):
                    model = model.split(".")[0]
                    if model in app_models:
                        print(f"\tClearing {app}_{model}...")
                        clear_table(app, model)
            print("[OK]\n")

        # Insert tables
        if "--no_insert" not in sys.argv:
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
