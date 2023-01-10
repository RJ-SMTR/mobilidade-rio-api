"""
query_utils.py
Basic helpers to query gtfs data from database, and basic functions to help with queries
"""
import os
import hashlib

# generate random names for subqueries


def q_random_hash(prefix="q", hash_len=32):
    """Generate random hash name for subqueries"""
    ret = f"{prefix}__{hashlib.md5(os.urandom(hash_len)).hexdigest()[:hash_len]}"
    return ret


def q_limit(query: str, limit: int, external: bool = False):
    """
    q_limit v0.1 - 2022/12/26
    Limit query results

    Params:
        query (str): query to limit
        limit (int): limit value
        external (bool): if True, will wrap query in a subquery
            Default: False
    """
    if external:
        return f"SELECT * FROM ({query}) as {q_random_hash()} \nLIMIT {limit}"
    else:
        return f"{query} \nLIMIT {limit}"


def q_cols_match_all(
    table,
    unique_cols: list,
    col_match_all: list,
    col_in: dict = None,
    select: list = "*",
    table_is_query: bool = False,
    q_conditions: str = None,
):
    """
    v0.4 - 2023/01/04
    Get unique combinations of columns and select other columns

    Parameters
        table : str
        unique_cols : list | str
        select_cols : list | str

        col_match_all : dict -> {str: list, ...}
            Filter by cols that match all conditions individually

        col_in (optional) : dict -> {str: list, ...}
            Filter if each col has a list of values
            Recommended way to filter in this query

        table_is_query (optional) : bool
            If True, will wrap table in a subquery

        q_conditions (optional) : str
            Additional conditions to include in query
            TODO: filter each condition individually too
    """

    # if cols is a list, convert to string
    if isinstance(unique_cols, list):
        unique_cols = ",".join(unique_cols)
    if isinstance(select, list):
        select = ",".join(select)

    # select cols in query and subquery
    select_cols_1 = select
    select_cols_2 = select.replace("row_num", "").replace(",,", ",")
    if select_cols_2[-1] == ",":
        select_cols_2 = select_cols_2[:-1]

    # validate q_conditions
    q_conditions = "\n" + " " * 12 + f"AND {q_conditions}" if q_conditions else ""

    # wrap table in a subquery
    if table_is_query:
        table = f"({table}) as {q_random_hash()}"

    # filter col_match_all
    if None not in (col_match_all, col_in):
        # AND col1 IN ( (SELECT DISTINCT ...) INTERSECT (...) ...) AND col_2 IN ...
        col_match_all = [
            f" {col} IN ("
            + " INTERSECT ".join(
                [
                    f"(SELECT DISTINCT {col} FROM {table} "
                    + f"WHERE {col_1} = {str([value])[1:-1]})"  # add quotes if str
                    for col_1 in col_in
                    for value in col_in[col_1]
                ]
            )
            + ")"
            for col in col_match_all
        ]
        col_match_all = "AND " + " AND ".join(col_match_all)
    else:
        col_match_all = ""

    # filter col_values
    if col_in is not None:
        # WHERE col1 IN (...) AND col2 IN (...) AND ...
        col_in = " AND ".join(
            [f"{col} IN ({str(list(values))[1:-1]})" for col, values in col_in.items()]
        )
        col_in = f"WHERE {col_in}"
    else:
        col_in = ""

    return f"""
    SELECT {select_cols_1} FROM (
        SELECT *,
            ROW_NUMBER() OVER (PARTITION BY {unique_cols} ORDER BY id) AS row_num
        FROM {table}
        {col_in}{q_conditions}
        {col_match_all}
    ) AS {q_random_hash()}
    WHERE row_num = 1
    """
