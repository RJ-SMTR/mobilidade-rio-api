
SQL_WORDS = [
    'SELECT',
    'AS ',
    'WHERE',
    'CAST',
    'DATE',
    'ASC',
    'DESC',
    'LEFT',
    'RIGHT',
    'INNER',
    'STIRNG',
    'FROM',
    'ORDER',
    'GROUP',
    'BY',
    'LIMIT',
    'OFFSET',
    'COUNT',
    'AND',
    'DISTINCT',
]

SQL_METHODS = [
    'COUNT'
]

def format_sql_query(sql_query: str) -> str:
    """Formats a SQL query by highlighting keywords and methods.

    Args:
        sql_query: The SQL query string to format.

    Returns:
        The formatted SQL query string with keywords and methods highlighted.
    """

    new_str = sql_query
    for keyword in SQL_WORDS:
        # Use ANSI escape codes for color (replace with your desired formatting)
        new_str = new_str.replace(
            f"\\b{keyword}\\b", f"\033[1;34m{keyword}\033[0m")
    for method in SQL_METHODS:
        # Use ANSI escape codes for color (replace with your desired formatting)
        new_str = new_str.replace(
            f"\\b{method}\\b", f"\033[1;35m{method}\033[0m")
    return new_str
