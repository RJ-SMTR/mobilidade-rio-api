"""database_utils.py"""

import csv
import io
import logging
from typing import IO

logger = logging.getLogger("database_utils")


def parse_col_fk_names(col: str, check_names: list = None) -> str:
    """Replace many `col_id` to `col_id_id`"""
    new_col = col
    if check_names:
        for name in check_names:
            new_col = new_col.replace(name, name + "_id")
    return new_col


def parse_header_fk_names(header: list[str], check_names: list = None) -> str:
    """For every column rename fks like `stop_id` to `stop_id_id`"""
    return [parse_col_fk_names(col, check_names) for col in header]


def get_csv_table_cols(file: IO[bytes], fks: list = None) -> list[str]:
    """
    From csv table get table columns, with conversions if necessary

    Parameters:
        fks: convert foreing key columns like `stop_id` to `stop_id_id`
    """
    wrapper = io.TextIOWrapper(file, encoding='utf-8')
    reader = csv.reader(io.TextIOWrapper(file, encoding='utf-8'))
    header = next(reader)
    cols = [parse_col_fk_names(col, fks) for col in header]
    wrapper.seek(0)
    file = wrapper
    return cols


def parse_existing_cols(compare_cols: list[str], existing_cols: list[str]):
    """Ignore not-existing columns"""
    cols = [c for c in compare_cols if c in existing_cols]
    return cols
    # cols = compare_cols.copy()
    # for i in range(len(compare_cols) - 1, -1, -1):
    #     if cols[i] not in existing_cols:
    #         cols.pop(i)
    #     else:
    #         break
    # return cols

