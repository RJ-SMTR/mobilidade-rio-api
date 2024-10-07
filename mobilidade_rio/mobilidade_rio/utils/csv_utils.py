import csv
import io
from typing import IO

import pandas as pd
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

# pylint: disable=no-name-in-module,E0401
from mobilidade_rio.utils.file_utils import remove_file_if_exists


def get_csv_header(file: IO[bytes]) -> list[str]:
    """
    From csv table get table columns, with conversions if necessary

    Parameters:
        fks: convert foreing key columns like `stop_id` to `stop_id_id`
    """
    reader = csv.reader(io.TextIOWrapper(file, encoding='utf-8'))
    header = next(reader)
    return header


# def filter_csv_columns(csv_bytes: IO[bytes], cols: list[str], chunksize=1000) -> tuple[IO[bytes], str]:
#     """Filter columns from csv IO (with header), then return a new IO"""
#     with NamedTemporaryFile(mode='w+', suffix='.csv') as temp_file:
#         temp_file.write(','.join(cols) + '\n')
#         for chunk in pd.read_csv(csv_bytes, chunksize=chunksize):
#             filtered_chunk: pd.DataFrame = chunk[cols]
#             filtered_chunk.to_csv(temp_file, index=False, header=False)
#         temp_file.seek(0)
#         new_csv_bytes = io.BytesIO(temp_file.read().encode('utf-8'))
#         filename = temp_file.name
#     return filename, new_csv_bytes


def filter_csv_columns(csv_bytes: IO[bytes], cols: list[str], chunksize=1000):
    """Filter columns from csv IO (with header), then return a new IO"""
    file_name = 'upload_gtfs_temp.csv'
    _write_csv_header(file_name, cols)
    for chunk in pd.read_csv(csv_bytes, chunksize=chunksize):
        chunk.columns = rename_df_cols(cols, chunk)
        filtered_chunk: pd.DataFrame = chunk[cols]
        _append_df_to_csv(filtered_chunk, file_name)
    final_output = io.BytesIO(default_storage.open(file_name).read())
    return final_output


def _write_csv_header(file_name: str, cols: list[str]):
    """Overwrite a new csv by writing header"""
    filtered_csv = io.BytesIO()
    filtered_csv.write(','.join(cols).encode('utf-8') + b'\n')
    remove_file_if_exists(file_name)
    default_storage.save(file_name, ContentFile(filtered_csv.getvalue()))


def _append_df_to_csv(chunk: pd.DataFrame, file_name: str):
    chunk_io = io.BytesIO()
    chunk.to_csv(chunk_io, index=False, header=False)
    with default_storage.open(file_name, 'ab') as f:
        f.write(chunk_io.getvalue())


def rename_df_cols(cols: list[str], df: pd.DataFrame):
    """Merge rename df cols with new columns by index"""
    df_cols = df.columns
    new_cols: list[str] = []
    for i, df_col in enumerate(df_cols):
        new_cols.append(df_col if i >= len(cols) else cols[i])
    return new_cols
