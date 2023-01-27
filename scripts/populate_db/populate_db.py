"""
populate_db
v1.0 - 02/12/2022

Copy CSV to Postgres

How to use:

- Put csv files in `csv_files` folder
- Run script

"""

import json
import sys
import os
import io
import psycopg2
import pandas as pd

parameters = """\
-d --empty_db           Empty database           [<drop_all>]
-e --empty_tables       Empty all tables         [<empty_tables>]
-i --no_insert          Don't insert data        [<no_insert>]
-p --port
-t --drop_tables        Drop tables in list      [<drop_tables>]
"""

remove_duplicate_cols = {
    "pontos_trips": [
        "trip_id"
    ]
}

validate_cols = {
    "pontos_stoptimes": [
        "trip_id"
    ],
    "pontos_trips": [
        "trip_id"
    ]
}

script_path = os.path.dirname(os.path.abspath(__file__))
current_path = os.getcwd()

def print_colored(color, *args, **kwargs):
    """Print text in color"""
    colors = {
        "red": "\033[91m", "green": "\033[92m", "yellow": "\033[93m", "blue": "\033[94m",
        "purple": "\033[95m", "cyan": "\033[96m", "white": "\033[97m", "black": "\033[98m",
        "end": "\033[0m", "orange": "\033[38;5;208m", "back": "\b",
    }
    if color in colors:
        color = colors[color]
    # print color with no space after
    print(f"{color}{args[0]}", end="")
    # print rest of args
    print(*args[1:], colors['end'], **kwargs)


def convert_to_type(
    data,
    initial_type: type=None,
    ret_type: type=io.TextIOWrapper,
    save_file_name: str = None,
    ):

    """Return data from type"""

    if initial_type is None:
        initial_type = type(data)
    file_name = "temp.txt"

    save_file_path = None
    if save_file_name is not None:
        # crete ./logs folder if not exists
        if not os.path.exists(script_path + "/logs"):
            os.makedirs(script_path + "/logs")
        save_file_path = os.path.join(script_path, "logs", save_file_name)


    # return DataFrame
    if ret_type == pd.DataFrame or (ret_type is None and initial_type == pd.DataFrame):
        if isinstance(data, pd.DataFrame):
            if save_file_name is not None:
                data.to_csv(save_file_path, index=False, header=False)
            return data
        else:
            data = pd.read_csv(data)
            if save_file_name is not None:
                data.to_csv(save_file_path, index=False, header=False)
            return data

    # return Text
    elif ret_type == io.TextIOWrapper or (ret_type is None and initial_type == io.TextIOWrapper):
        if isinstance(data, io.TextIOWrapper):
            if save_file_name is not None:
                with open(save_file_path, 'w', encoding="utf8") as f_1:
                    f_1.write(data.read())
                    f_1.seek(0)
            return data
        else:
            file_path_1 = os.path.join(script_path, file_name)
            data.to_csv(file_path_1, index=False, header=False)
            if save_file_name is not None:
                data.to_csv(save_file_path, index=False, header=False)
            return open(file_path_1, 'r', encoding="utf8")
    exit()


def validate_col_names(_table_name: str, cols: list() = None) -> list():
    """Test if column name is in table with common tricks"""
    cur.execute(f"SELECT column_name FROM information_schema.columns \
        WHERE table_name = '{_table_name}';")
    query_cols = cur.fetchall()
    query_cols = [col[0] for col in query_cols]

    if cols is None:
        return query_cols

    # for each col, test different tricks and return the correct one
    for col in cols:
        if col not in query_cols:
            col_1 = f"{col}_id"
            if col_1 in query_cols:
                # change col name
                i_1 = cols.index(col)
                cols[i_1] = col_1
    return cols


def validate_table_name(_table: str, _app: str = "") -> str:
    """Test if table exists, or try another combination"""
    # if app, table = app_table
    if _app:
        _table = f"{_app}_{_table}"
    table_prefix = _table.split("_")[0]
    table_remaining = _table[len(table_prefix) + 1:]
    _table = f"{table_prefix}_{table_remaining.replace('_', '')}"
    return _table


def validate_col_values(
    data,
    table_name: str,
    cols: list = None,
    ret_type: str = None,
    remove_duplicates: bool = True,
):
    """
    Filter columns before upload

    Args:
        data (io.TextIOWrapper | pandas.DataFrame): data input
        table_name (str): table name
        cols (list): columns to validate
        ret_type (str): choose between dataframe (df) or raw data (str)
            default is None, returns the same type as the input

    Returns:
        filtered data (io.TextIOWrapper | pandas.DataFrame):
            filtered data output
    """
    # if data is a string, read it as csv
    data_type = type(data)
    if data_type != pd.DataFrame:
        # read data without index
        data = pd.read_csv(
            data, sep=",", encoding="utf8", low_memory=False, dtype=str)
    if cols is None:
        cols = [col for col in data.columns]
    cols = validate_col_names(table_name, cols)
    data.columns = cols

    len_history = [len(data)]

    # remove duplicates
    remove_duplicate_cols_table_commas = []
    remove_duplicate_cols_table_no_commas = []
    if table_name in remove_duplicate_cols:
        # separate cols with commas, without and unique
        for col in remove_duplicate_cols[table_name]:
            if "," in col:
                cols_1 = validate_col_names(table_name, col.split(","))
                remove_duplicate_cols_table_commas.append(cols_1)
            else:
                remove_duplicate_cols_table_no_commas.append(col)
        remove_duplicate_cols_table_no_commas = validate_col_names(
            table_name, remove_duplicate_cols_table_no_commas)

    # validate cols
    validade_cols_table = []
    if table_name in validate_cols:
        validade_cols_table = validate_col_names(
            table_name, validate_cols[table_name])

    # remove_cols_containing
    remove_cols_containing = []
    remove_cols_containing_table = []
    if 'remove_cols_containing' in settings:
        remove_cols_containing = settings['remove_cols_containing']
        if table_name in remove_cols_containing:
            remove_cols_containing_table = remove_cols_containing[table_name]
            # validate cols for each table
            remove_cols_containing_table = validate_col_names(
                table_name, remove_cols_containing_table)

    # enforce types
    cols_set_types = []
    if 'enforce_type_cols' in settings and table_name in settings['enforce_type_cols']:
        cols_map = settings['enforce_type_cols'][table_name]
        col_names = list(cols_map.keys())
        # to int
        cols_int = [k for k,v in cols_map.items() if 'int' in v]
        data[cols_int] = data[cols_int].fillna(0)
        data[col_names] = data[col_names].apply(pd.to_numeric, errors='ignore')
        # to other types
        data = data.astype(settings['enforce_type_cols'][table_name]).copy()
        # TODO: get types from database
        # cols_1 = validate_col_types(table_name, data.columns)

    # drop null
    if 'drop_null_cols' in settings and table_name in settings['drop_null_cols']:
        data = data.dropna(subset=settings['drop_null_cols'][table_name]).copy()

    # run validate cols
    if (table_name in validate_cols
        or table_name in remove_duplicate_cols
        or table_name in remove_cols_containing):
        for col in cols:
            if col in validade_cols_table:
                # ? if value ends with _1, split and remove _1
                data[col] = data[col].str.split("_1").str[0]
                data = data.copy()
                # ? Debug
                # data = data[data[col].str.contains("2") == False]
                # ?remove row if contains _<n> except _1
                data = data[~data[col].str.contains("_")].copy()

            # remove duplicates
            if remove_duplicates and col in remove_duplicate_cols_table_no_commas:
                data = data.drop_duplicates(subset=[col]).copy()

            # convert to type
            if col in cols_set_types:
                if cols_set_types[col] == "int":
                    data[col] = data[col].astype("Int64")

            # remove cols containing
            if col in remove_cols_containing_table:
                print(f"Removing_cols_containing: {col}")
                # drop rows if col value contains part of substring
                for substring in remove_cols_containing_table[col]:
                    data = data[~data[col].str.contains(substring)].copy()

        # remove duplicates with commas
        if remove_duplicates and remove_duplicate_cols_table_commas:
            for cols_1 in remove_duplicate_cols_table_commas:
                data = data.drop_duplicates(subset=cols_1).copy()

    len_history.append(len(data))
    # ? debug
    # print("CVC hist", len_history)

    return convert_to_type(data, data_type, ret_type, table_name + ".txt")


def upload_data(_app: str, _model: str):
    """
    Upload data to Postgres

    Args:
        app (str): app name
        model (str): model name
        flag_params (str): flag parameters

    Returns:
        None
    """

    def constraint_err(detail:str):
        if not detail:
            return
        return [i for i in ["Key ", " is not present in table ", "constraint"] if i in detail]

    table_name = f"{_app}_{_model.replace('_', '')}"
    file_path_1 = os.path.join(folder, f"{_model}.txt")

    if os.path.isfile(file_path_1):
        print(f"Table '{table_name}'")
        with open(file_path_1, 'r', encoding="utf8") as f_1:
            # if type is _io.TextIOWrapper
            # Filter table
            print("Filtering...")
            cols = f_1.readline().strip().split(',')
            cols = validate_col_names(table_name, cols)
            f_1.seek(0)
            data = validate_col_values(f_1, table_name, cols)
            if "--no_insert" in sys.argv:
                return
            # insert data
            print("inserting ...")
            sql = f"""
                COPY {table_name} ({','.join(cols)})
                FROM STDIN WITH CSV DELIMITER AS ','
            """
            try:
                if "--no_insert" not in sys.argv and '-i' not in sys.argv:
                    cur.copy_expert(sql, data)
                    conn.commit()
                print("[OK]")

            except psycopg2.Error as error:
                conn.rollback()
                print_colored("yellow","Error on copy data:")
                detail = error.diag.message_detail
                if not detail:
                    detail = str(error).strip()
                # diag.message_detail comes from psycopg2
                print_colored("yellow", error, end='')
                print_colored("yellow", "Retrying manually...")
                # write error to file
                log_path = os.path.join(script_path, "logs", f"{table_name}_error.log")
                with open(log_path, 'w', encoding="utf8") as f_2:
                    f_2.write(detail)
                    f_2.write("\nRetrying manually...\n")

                # if detail is "fk not present in table"
                count_1 = 0
                if constraint_err(detail):
                    # try catch per line
                    f_1.seek(0)
                    total = f_1.readlines()
                    f_1.seek(0)
                    cols = f_1.readline().strip().split(',')
                    cols = validate_col_names(table_name, cols)
                    temp_path = os.path.join(script_path, "temp.txt")
                    with open(temp_path, 'r', encoding="utf8") as f_temp:
                        data = validate_col_values(f_temp, table_name, cols)
                    # iterate lines
                    for line in data:
                        try:
                            cur.copy_from(
                                file=io.StringIO(line),
                                table=table_name,
                                sep=",",
                                columns=cols
                            )
                            conn.commit()
                            count_1 += 1
                        except psycopg2.Error:
                            conn.rollback()
                            try:
                                # copy expert, for null values
                                sql_1 = f"""
                                COPY {table_name} ({','.join(cols)})
                                FROM STDIN WITH CSV DELIMITER AS ','
                                """
                                cur.copy_expert(sql_1, io.StringIO(line))
                                conn.commit()
                                count_1 += 1
                            except psycopg2.Error as error_2:
                                # write error to file
                                with open(log_path, 'a', encoding="utf8") as f_2:
                                    f_2.write(str(error_2))
                                    f_2.write("\n")
                                conn.rollback()
                                if constraint_err(error_2.diag.message_detail):
                                    pass
                                else:
                                    raise error_2
                if count_1 == 0:
                    print_colored("red","[FAIL - NO INSERT]")
                else:
                    print(f"[OK - {count_1}/{len(total)}]")
    print()


def help_1():
    """Help"""
    print("Usage: populate_db.py [options]")
    print(parameters)


if __name__ == "__main__":

    # Setting default parameters

    csv_path = os.path.join(script_path, "csv_files")
    file_path = os.path.join(script_path, "settings.json")

    try:
        # if file exists
        with open(file_path, "r", encoding="utf8") as f:
            settings = json.load(f)
    except FileNotFoundError:
        # raise string
        print_colored("red", "File not found: settings.json")

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
                found = param.find("[")
                if found != -1:
                    param = param[:param.find("[")]
            parameters_new += param + "\n"
        parameters = parameters_new
    if 'remove_duplicate_cols' in settings:
        # append
        remove_duplicate_cols = settings['remove_duplicate_cols']
    if 'validate_cols' in settings:
        # append
        validate_cols = settings['validate_cols']
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
    if "--empty_db" in sys.argv or "-d" in sys.argv:
        print("Dropping schema...")
        cur.execute("DROP SCHEMA IF EXISTS public CASCADE")
        conn.commit()
        print("Creating schema...")
        cur.execute("CREATE SCHEMA IF NOT EXISTS public")
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
        if (("-e" in sys.argv or "--empty_tables" in sys.argv\
        or "empty_tables" in settings["flag_params"])and\
            "-e=false" not in sys.argv and "--empty_tables=false" not in sys.argv):
            print(f"Clearing all tables in {app}:")
            if app in settings["table_order"].keys():
                folder = os.path.join(csv_path, app)
                app_models = settings["table_order"][app]
                for model in os.listdir(folder):
                    model = model.split(".")[0]
                    if model in app_models:
                        print(f"\tClearing {app}_{model}...")
                        table = validate_table_name(model, app)
                        cur.execute(f"TRUNCATE {table} CASCADE")
                        conn.commit()
            print("[OK]\n")

        # Insert tables
        if app in settings["table_order"].keys():
            folder = os.path.join(csv_path, app)
            app_models = settings["table_order"][app]

            folder_dirs = [f.split(".")[0] for f in os.listdir(folder)]
            for model in app_models:
                if model in folder_dirs:
                    model = model.split(".")[0]
                    upload_data(app, model)
        else:
            print(
                f"Couldn't find {app} in 'settings.json'.\n\
                Make sure you have the correct app name - \
                should be a folder in mobilidade_rio/mobilidade_rio."
            )
