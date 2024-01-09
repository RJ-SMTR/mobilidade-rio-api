"""
populate_db

Copy CSV to Postgres

How to use:

- Put csv files in `csv_files` folder
- Run script

"""

import sys
import os
import shutil
import io
import yaml
import psycopg2
import pandas as pd

# TODO: use argparse
PARAMETERS = """\
-d --empty_db           Empty database                      [<empty_db>]
-e --empty_tables       Empty all tables                    [<empty_tables>]
-m --merge_tables       Merge tables in any app subfolder   [<merge_tables>]
-n --no_insert          Don't insert data                   [<no_insert>]
-p --port
-t --drop_tables        Drop tables in list                 [<drop_tables>]
"""

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
TAB = " "*4

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


def mkdir_if_not_exists(path):
    """Create folder if not exists"""
    if not os.path.exists(path):
        os.makedirs(path)


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
        mkdir_if_not_exists(script_path + "/logs")
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

    # validate cols
    validate_cols_table = []
    if table_name in validate_cols:
        validate_cols_table = validate_col_names(
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
    if settings.get('enforce_type_cols').get(table_name):
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
        or (settings.get('remove_duplicate_cols') and 
            table_name in settings.get('remove_duplicate_cols').keys())
        or table_name in remove_cols_containing):

        # remove duplicates
        duplicate_cols = settings.get('remove_duplicate_cols').get(table_name)
        if duplicate_cols:
            duplicate_cols =validate_col_names(table_name, duplicate_cols)
            data = data.drop_duplicates(subset=duplicate_cols).copy()

        # per col
        for col in cols:
            if col in validate_cols_table:
                # ? if value ends with _1, split and remove _1
                data[col] = data[col].str.split("_1").str[0]
                data = data.copy()
                # ? Debug
                # data = data[data[col].str.contains("2") == False]
                # ?remove row if contains _<n> except _1
                data = data[~data[col].str.contains("_")].copy()

            # convert to type
            if col in cols_set_types:
                if cols_set_types[col] == "int":
                    data[col] = data[col].astype("Int64")

            # remove cols containing
            if col in remove_cols_containing_table:
                # drop rows if col value contains part of substring
                for substring in remove_cols_containing_table[col]:
                    data = data[~data[col].str.contains(substring)].copy()

    len_history.append(len(data))
    # ? debug
    # print("CVC hist", len_history)

    return convert_to_type(data, data_type, ret_type, f"{table_name}.{settings['table_extension']}")


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
    file_path_1 = os.path.join(folder, f"{_model}.{settings['table_extension']}")
    print(f"{TAB}Table '{table_name}'")
    if os.path.isfile(file_path_1):
        with open(file_path_1, 'r', encoding="utf8") as f_1:
            # Filter table
            print(f"{TAB}Filtering...")
            cols = f_1.readline().strip().split(',')
            cols = validate_col_names(table_name, cols)
            f_1.seek(0)
            data = validate_col_values(f_1, table_name, cols)
            if "--no_insert" in sys.argv or '-n' in sys.argv:
                return
            # insert data
            print(f"{TAB}Inserting ...")
            sql = f"""
                COPY {table_name} ({','.join(cols)})
                FROM STDIN WITH CSV DELIMITER AS ','
            """
            try:
                if "--no_insert" not in sys.argv and '-n' not in sys.argv:
                    cur.copy_expert(sql, data)
                    conn.commit()
                else:
                    print(f"{TAB}[OK - no insert]")

            except psycopg2.Error as error:
                conn.rollback()
                print_colored("yellow",f"{TAB}Error on copy data:")
                detail = error.diag.message_detail
                if not detail:
                    detail = str(error).strip()
                # diag.message_detail comes from psycopg2
                print_colored("yellow", f"{TAB}{error}", end='')
                print_colored("yellow", f"{TAB}Retrying manually...")
                # write error to file
                log_path = os.path.join(script_path, "logs", f"{table_name}_error.log")
                with open(log_path, 'w', encoding="utf8") as f_2:
                    f_2.write("ERROR:" + str(error))
                    f_2.write("\nRetrying manually...\n")

                # if detail is "fk not present in table"
                count_1 = 0
                # if constraint_err(detail):
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
                            # if constraint_err(error_2.diag.message_detail):
                            #     pass
                            # else:
                            #     raise error_2
                if count_1 == 0:
                    print_colored("red",f"{TAB}[FAIL - NO INSERT]")
                else:
                    print(f"{TAB}[OK - {count_1}/{len(total)}]")
    else:
        print_colored("red",f"{TAB}[FAIL - NOT FOUND]")
    print()


def help_1():
    """Help"""
    print("Usage: populate_db.py [options]")
    print(PARAMETERS)


def empty_folder(folder_path):
    "empty folder"
    for filename in os.listdir(folder_path):
        file_path_1 = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path_1) or os.path.islink(file_path_1):
                os.unlink(file_path_1)
            elif os.path.isdir(file_path_1):
                shutil.rmtree(file_path_1)
        except shutil.Error as shutil_error:
            print(f'Failed to delete {file_path_1}. Reason: {shutil_error}')


def merge_tables(app_folder, table_name, table_extension):
    "Merge tables from tables in subfolder"
    merged_df = pd.DataFrame()
    for subfolder in os.listdir(app_folder):
        if os.path.isdir(os.path.join(app_folder,subfolder)):
            for table_file in os.listdir(f"{app_folder}/{subfolder}"):
                table_name_file = table_file.split('.')[0]
                if table_file.endswith(table_extension) and table_name_file == table_name:

                    filepath = os.path.join(app_folder, subfolder, table_file)
                    df = pd.read_csv(filepath)
                    # Merge
                    if not merged_df.empty:
                        merged_df = pd.concat([merged_df,df], ignore_index=True)
                    else:
                        merged_df = df.copy()

    # Save the merged tables to the output folder
    filename = os.path.join(app_folder, f'{table_name}.{table_extension}')
    merged_df.to_csv(filename, index=False)


if __name__ == "__main__":

    # Setting default parameters

    TABLES_FOLDER = "fixtures"
    tables_path = os.path.join(script_path, TABLES_FOLDER)
    SETTINGS_FILE = "populate_db.yaml"
    if not os.path.isfile(os.path.join(script_path,SETTINGS_FILE)):
        print_colored("red", f"File not found: {SETTINGS_FILE}")
        exit(1)
    else:
        file_path = os.path.join(script_path, SETTINGS_FILE)
        with open(file_path, "r", encoding="utf8") as f:
            settings = yaml.safe_load(f)

    # update parameters if exists in settings[param]
    # if flag_params in settings:
        for param in settings.keys():
            if f"--{param} " in PARAMETERS:
                if settings.get(param):
                    PARAMETERS = PARAMETERS.replace(f"<{param}>", "ACTIVE")

        # remove all from "[" if this line is not [ACTIVE]
        PARAMETERS_NEW = ""
        for param in PARAMETERS.split("\n"):
            if "ACTIVE" not in param:
                found = param.find("[")
                if found != -1:
                    param = param[:param.find("[")]
            PARAMETERS_NEW += param + "\n"
        PARAMETERS = PARAMETERS_NEW

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

    # param port
    _params = [p for p in ("-p","--port") if p in sys.argv]
    if _params:
        db_params["port"] = sys.argv[list(sys.argv).index(_params[0])+1]

    # Create folders if not exist
    mkdirs = ["logs", "fixtures"]
    for folder in mkdirs:
        mkdir_if_not_exists(f"{script_path}/{folder}")

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


    # Tables found
    tables_found = []
    total_tables = []
    comment_tables = []
    for app in settings["table_order"].keys():
        if not settings["table_order"] or not settings["table_order"][app]:
            continue
        for table in settings["table_order"][app]:
            if table.startswith("#"):
                comment_tables.append(table)
            else:
                total_tables.append(table)


    # Merge tables
    if "--merge_tables" in sys.argv or "-m" in sys.argv or \
        settings.get("merge_tables"):
        print("Merging tables...")
        for app in os.listdir(tables_path):
            if not app in settings["table_order"] or not settings["table_order"][app]:
                continue
            app_models = settings["table_order"][app]
            for model in app_models:
                print(f"{TAB}Merging {app}/{model}.{settings['table_extension']}")
                merge_tables(os.path.join(tables_path,app), model, settings['table_extension'])
        
        if "--merge_tables" in sys.argv or "-m" in sys.argv:
            exit(0)

    if settings.get("clear_logs"):
        empty_folder(os.path.join(script_path,"logs"))

    # Update data from files in tables folder
    for app in os.listdir(tables_path):

        # if not key or not values
        if not app in settings["table_order"] or not settings["table_order"][app]:
            continue

        # get tables found
        if app in settings["table_order"].keys():
            folder = os.path.join(tables_path, app)
            app_models = settings["table_order"][app]
            for model in os.listdir(folder):
                model = model.split(".")[0]
                if model in app_models:
                    tables_found.append(model)

        # drop all related tables then exit
        if "--drop_tables" in sys.argv or "-t" in sys.argv:
            # if table exists
            cur.execute("SELECT table_name FROM information_schema.tables \
                            WHERE table_schema = 'public'")
            tables = cur.fetchall()
            print(f"Dropping related tables in {app}:")
            COUNT = 0


            if app in settings["table_order"].keys():
                folder = os.path.join(tables_path, app)
                app_models = settings["table_order"][app]
                for model in os.listdir(folder):
                    model = model.split(".")[0].replace("_", "")
                    if model in app_models and f"{app}_{model}" in tables:
                        print(f"{TAB}Dropping {app}_{model}...")
                        cur.execute(
                            f"DROP TABLE IF EXISTS {app}_{model} CASCADE")
                        # drop if exists
                        conn.commit()
                        COUNT += 1
            if not COUNT:
                print(f"{TAB}No related tables found.")
            continue

        # Clear all tables
        EMPTY_TABLE = ("-e" in sys.argv or "--empty_tables" in sys.argv or settings.get("empty_tables"))
        if EMPTY_TABLE:
            print(f"Clearing all tables in {app}:")
            if app in settings["table_order"].keys():
                folder = os.path.join(tables_path, app)
                app_models = settings["table_order"][app]
                for model in os.listdir(folder):
                    model = model.split(".")[0]
                    if model in app_models:
                        print(f"{TAB}Clearing {app}_{model}...")
                        table = validate_table_name(model, app)
                        cur.execute(f"TRUNCATE {table} CASCADE")
                        conn.commit()
            print("[OK]\n")
            if "-e" in sys.argv or "--empty_tables" in sys.argv:
                exit(0)

        # Insert tables
        print(f"Inserting all tables in {app}:")
        if app in settings["table_order"].keys():
            folder = os.path.join(tables_path, app)
            app_models = settings["table_order"][app]
            folder_dirs = [f.split(".")[0] for f in os.listdir(folder)]
            for model in app_models:
                if model in folder_dirs:
                    model = model.split(".")[0]
                    upload_data(app, model)
        else:
            if "." in app:
                print_colored("red", f"The file '{app}' is inside '{TABLES_FOLDER}'.\n"
                    f"This script only read tables in '{TABLES_FOLDER}'/<django app>' folders\n")
            else:
                print_colored("red",
                f"ERROR: The folder '{app}' is inside '{TABLES_FOLDER}' folder, "
                f"but it's not configured in settings key [table_order]\n"
                )

    # Validate tables

    tables_not_found = [table for table in total_tables if table not in tables_found]
    if tables_not_found:
        print_colored("red", "ERROR: The following tables were not found:")
        for table in tables_not_found:
            print_colored("red", TAB,table)
        print()
        print_colored("red", f"{TAB}Tip: Table name in settings and in '{TABLES_FOLDER}' folder must match the db.")
        print_colored("red", f"{TAB}Tip: Check file extension and compare with settings, default is txt.")
        print()

    if comment_tables:
        print_colored("yellow", "You have commented out the following tables:")
        for table in comment_tables:
            print_colored("yellow", TAB,table)
        print()
