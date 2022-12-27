"""
gtfs_queries.py
Helpers to query gtfs data from database, and basic functions to help with queries
All raw query utils, not only gtfs related, because they are used in gtfs queries
"""
import os
import hashlib

# Jupyter
import psycopg2
from IPython.display import display, HTML

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


def q_col_in(
    where_col_in: dict,
    select: list = None,
    from_target: str = None,
    order_by: list = None,
    target_is_query: bool = True,
) -> str:
    """
    get_col_in v0.2 - 2022/12/26
    Select target if cols have values

    Params
        select (list|str): list of columns to select
            '*' is accepted as value
            Example: ["col1", "col2", "col3"]
            SQL: SELECT col1, col2, col3

        from_table (str): table name to select and get column names

        where_col_in (dict): dict with columns and values to filter
            Dict format: {str: list, ...}
            Example: {"col1": ["val1", '2', 14], "col2": ["val3"]}
            SQL: col1 IN ('val1', '2', 14) AND col2 IN ('val3')

        order_by (list|str): list of columns to order by

        target_is_query (bool): if True, will wrap from_target in a subquery

    Returns
        if select, from_target, where_col_in are not None:
            SELECT {select} FROM {from_target} WHERE {where_col_in} ...
        else:
            <col1> IN (<values>) AND <col2> IN (<values>), ...

    Obs
        you need to pass the real db table and cols' names
    """

    # validate params
    if isinstance(select, list):
        select = ", ".join(select)
    if target_is_query:
        from_target = f"({from_target}) as {q_random_hash()}"

    if order_by:
        if isinstance(order_by, (list, tuple)):
            order_by = ", ".join(order_by)
        order_by = f" \nORDER BY {order_by}"
    else:
        order_by = ""

    col_in = " \nAND ".join(
        [
            f"{col} IN ({str(list(values))[1:-1]})"
            for col, values in where_col_in.items()
        ]
    )

    # build query
    if None in (select, from_target, where_col_in):
        return col_in
    else:
        return f"SELECT {select} \nFROM {from_target} \nWHERE " + col_in + order_by


def q_unique_cols(
    table,
    unique_cols: list,
    select: list = "*",
    col_in: dict = None,
    col_match_all: list = None,
    q_conditions: str = None,
):
    """
    v0.2 - 2022/12/26
    Get unique combinations of columns and select other columns

    Parameters
        table : str
        unique_cols : list | str
        select_cols : list | str

        col_in (optional) : dict -> {str: list, ...}
            Filter if each col has a list of values
            Recommended way to filter in this query

        col_match_all (optional) : dict -> {str: list, ...}
            Filter by cols that match all conditions individually

        q_conditions (optional) : str
            Additional conditions to include in query
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


# Jupyter


def plot_query(cur: psycopg2.extensions.cursor, query: str):
    """Plot query results as html table in jupyter notebook"""
    cur.execute(query)
    # print len
    print(f"len: {cur.rowcount}")
    headers = [desc[0] for desc in cur.description]
    # print headers and results as html
    # format header with bold and color, like dataframe does with display()
    header_html = "".join(
        [
            f"<th style=\"font-weight:bold; background-color:'#ebebeb'\">{h}</th>"
            for h in headers
        ]
    )
    display(
        HTML(
            f"""
            <table>
                <tr>{header_html}</tr>
                {"".join([f"<tr>{''.join([f'<td>{c}</td>' for c in row])}</tr>"
                    for row in cur.fetchall()])}
            </table>
            """
        )
    )


def print_query(query):
    """for each line, print line number"""
    blue = "\033[94m"
    end = "\033[0m"
    # remove first line if is break line
    for i, line in enumerate(query.splitlines()):
        print(f"{blue}{i:03d}{end} {line}")
