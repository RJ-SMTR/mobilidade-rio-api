"""
utils_jupyter.py
Utils for jupyter notebook
"""

from django.db import connection
from IPython.display import display, HTML


def print_query_len(cur: connection.cursor, query: str):
    """Print len of query results"""
    cur.execute(query)
    return cur.rowcount


def plot_query(cur: connection.cursor, query: str, max_results=30):
    """
    Plot query results as html table in jupyter notebook

    Parameters:
        cur (connection.cursor): cursor to execute query
    """
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
    html_content = f"""
    <table>
        <tr>{header_html}</tr>
        {"".join([f"<tr>{''.join([f'<td>{c}</td>' for c in row])}</tr>"
            for row in cur.fetchall()[:max_results]])}
    </table>
    """

    display(HTML(html_content))


def print_query(query):
    """for each line, print line number"""
    blue = "\033[94m"
    end = "\033[0m"
    # remove first line if is break line
    for i, line in enumerate(query.splitlines()):
        print(f"{blue}{i+1:03d}{end} {line}")
