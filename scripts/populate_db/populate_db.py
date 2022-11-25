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

parameters = """\
-a --drop_all           Drop all tables          [<drop_all>]
-e --empty_tables       Empty all tables         [<empty_tables>]
-i --no_insert          Don't insert data        [<no_insert>]
-p --port
-t --drop_tables        Drop tables in list      [<drop_tables>]
"""

remove_duplicates_col = {
    "pontos_stop_times": {
        "trip_id"
    },
    "pontos_trips": {
        "trip_id"
    }
}


def validate_cols(table, cols: list()=None):
    """Test if column name is in table with common tricks"""
    cur.execute(f"SELECT column_name FROM information_schema.columns \
        WHERE table_name = '{table}';")
    query_cols = cur.fetchall()
    query_cols = [col[0] for col in query_cols]

    # for q_cols, if col not in columns, test with _id
    for q_col in query_cols:
        if q_col not in cols:
            if q_col + "_id" in cols:
                cols[cols.index(q_col + "_id")] = q_col

def validade_table(table:str, app:str=""):
    """Test if table exists, try another combination if not"""
    # if app, table = app_table
    if app:
        table = f"{app}_{table}"
    table_prefix = table.split("_")[0]
    table_remaining = table[len(table_prefix) + 1:]
    table = f"{table_prefix}_{table_remaining.replace('_', '')}"
    return table

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
            if validate_cols(col, table) in cols:
                dataframe = pandas.read_csv(
                    data, sep=",", encoding="utf8", low_memory=False)
                dataframe[col] = dataframe[col].str.split("_").str[0]
                dataframe = dataframe.drop_duplicates(subset=[col])
                print("FILTERING...")

                # save log csv file
                dataframe.to_csv(os.path.join(
                    folder, "temp.csv"), index=False, header=False)

                # save to postgres (exclude header)
                return open(os.path.join(folder, "temp.csv"), 'r', encoding="utf8")
    return data


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
        print(f"Table '{table_name}'")
        with open(file_path_1, 'r', encoding="utf8") as f_1:
            # Insert data
            if "--no_insert" not in sys.argv:
                # Filter table
                print("Filtering...")
                cols = f_1.readline().strip().split(',')
                validate_cols(table_name, cols)
                f_1.seek(1)
                data = filter_col(f_1, table_name, cols)
                # Insert table
                print("inserting ...")
                # copy with loading bar
                cur.copy_expert(f"COPY {table_name} ({','.join(cols)}) \
                                    FROM STDIN DELIMITER ',' CSV;", data)
                conn.commit()
    print("[OK]\n")


def help_1():
    """Help"""
    print("Usage: populate_db.py [options]")
    print(parameters)


if __name__ == "__main__":

    # Setting default parameters
    local_path = os.path.dirname(os.path.abspath(__file__))

    csv_path = os.path.join(local_path, "csv_files")
    file_path = os.path.join(local_path, "settings.json")

    try:
        with open(file_path, "r", encoding="utf8") as f:
            settings = json.load(f)
    except FileNotFoundError:
        # raise string
        print("Couldn't find settings.json file. Please create one and try again.")

    #  update parameters if exists in settings[param]
    # if flag_params in settings:
    if 'flag_params' in settings:
        for param in settings['flag_params']:
            if param in parameters:
                if settings['flag_params'] != "false":
                    parameters = parameters.replace(f"<{param}>", "ACTIVE")

        # remove all from "[" if this line is not [ACTIVE]
        parameters_new = ""
        for param in parameters.split("\n"):
            if "ACTIVE" not in param:
                param = param[:param.find("[")]
            parameters_new += param + "\n"
        parameters = parameters_new
    # Help
    if "--help" in sys.argv or "-h" in sys.argv:
        help_1()
        sys.exit(0)

    # Get postgres params
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

    # drop all tables from database
    if "--drop_all" in sys.argv or "-a" in sys.argv:
        print("Dropping schema...")
        cur.execute(f"DROP SCHEMA IF EXISTS public CASCADE")
        conn.commit()
        print("Creating schema...")
        cur.execute(f"CREATE SCHEMA IF NOT EXISTS public")
        conn.commit()
        exit(0)

    # Update data from files in csv_path
    for app in os.listdir(csv_path):

        # drop all related tables then exit
        if "--drop_tables" in sys.argv or "-t" in sys.argv:
            # if table exists
            cur.execute("SELECT table_name FROM information_schema.tables \
                            WHERE table_schema = 'public'")
            tables = cur.fetchall()
            print(f"Dropping related tables in {app}:")
            count = 0
            if app in settings["table_order"].keys():
                folder = os.path.join(csv_path, app)
                app_models = settings["table_order"][app]
                for model in os.listdir(folder):
                    model = model.split(".")[0].replace("_", "")
                    if model in app_models and f"{app}_{model}" in tables:
                        print(f"\tDropping {app}_{model}...")
                        cur.execute(
                            f"DROP TABLE IF EXISTS {app}_{model} CASCADE")
                        # drop if exists
                        conn.commit()
                        count += 1
            if not count:
                print("\tNo related tables found.")
            continue
        # Clear all tables
        if "--empty_tables" in sys.argv or '-e' in sys.argv or \
                "empty_tables" in settings["flag_params"]:
            print(f"Clearing all tables in {app}:")
            if app in settings["table_order"].keys():
                folder = os.path.join(csv_path, app)
                app_models = settings["table_order"][app]
                for model in os.listdir(folder):
                    model = model.split(".")[0]
                    if model in app_models:
                        print(f"\tClearing {app}_{model}...")
                        table = validade_table(model, app)
                        cur.execute(f"TRUNCATE {table} CASCADE")
                        conn.commit()
            print("[OK]\n")

        # Insert tables
        if "--no_insert" not in sys.argv and '-i' not in sys.argv:
            if app in settings["table_order"].keys():
                folder = os.path.join(csv_path, app)
                app_models = settings["table_order"][app]

                print(folder)
                folder_dirs = [f.split(".")[0] for f in os.listdir(folder)]
                for model in app_models:
                    if model in folder_dirs:
                        model = model.split(".")[0]
                        upload_data(app, model, flag_params)
            else:
                print(
                    f"Couldn't find {app} in 'settings.json'.\n\
                    Make sure you have the correct app name - \
                    should be a folder in mobilidade_rio/mobilidade_rio."
                )
