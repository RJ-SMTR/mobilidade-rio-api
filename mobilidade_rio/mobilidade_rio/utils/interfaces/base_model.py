from abc import abstractmethod
import csv
import io
from typing import IO, Any, Union

from django.conf import settings
from django.core.files.storage import default_storage
from django.db import connection, models
from django.db.models import Field, ForeignObjectRel, FloatField, BooleanField

from mobilidade_rio.utils.csv_utils import filter_csv_columns
from mobilidade_rio.utils.database_utils import (
    parse_existing_cols,
    parse_header_fk_names,
)


class BaseModel(models.Model):
    """Implement methods to upload csv"""

    foreign_keys: list[str] = []
    """Foreign key properties, used to rename with `_id` suffix in db query"""

    @classmethod
    def truncate(cls):
        """Truncate table."""
        db_table = cls._meta.db_table  # pylint: disable=no-member
        with connection.cursor() as cursor:
            cursor.execute(
                f"TRUNCATE TABLE {db_table} RESTART IDENTITY CASCADE;"
            )

    @classmethod
    def import_csv(cls, file: IO[bytes], header: list[str], orm=False):
        """Import data from a CSV file"""
        db_table = cls._meta.db_table  # pylint: disable=no-member
        treated_file, cols = cls._treat_csv(file, header)

        if orm:
            cls._import_csv_orm(file, header)
        else:
            with connection.cursor() as cursor:
                reader = csv.reader(io.TextIOWrapper(
                    treated_file, encoding='utf-8'))
                next(reader)
                file_no_header = io.StringIO(
                    '\n'.join([','.join(row) for row in reader]))
                cursor.copy_from(file_no_header, db_table,
                                 ",", columns=cols, null='')

    @classmethod
    def _import_csv_orm(cls, file: IO[bytes], header: list[str]):
        """Import csv using orm with chunks"""
        bulk_data = []
        reader = csv.DictReader(io.TextIOWrapper(file, encoding='utf-8'))
        for row in reader:
            item_kwargs = cls._get_orm_kwargs(header, row)
            bulk_data.append(cls(**item_kwargs))
        # pylint: disable=E1101
        cls.objects.bulk_create(bulk_data, batch_size=1000)

    @classmethod
    def _get_orm_kwargs(cls, cols_csv: list[str], row: dict):
        cols_db = parse_header_fk_names(cols_csv, cls.foreign_keys)
        kwargs = {}
        for i, col_db in enumerate(cols_db):
            kwargs[col_db] = cls._get_field_value(col_db, row[cols_csv[i]])
        return kwargs

    @classmethod
    def _get_field_name(cls, field: Union[Field, ForeignObjectRel]):
        return field.attname if hasattr(field, "attname") else field.field_name

    @classmethod
    def _get_field_value(cls, fieldname: str, value: Any):
        field = cls._meta.get_field(fieldname)  # pylint: disable=no-member
        field_type = field.get_internal_type()
        if field.is_relation:
            field_type = field.target_field.get_internal_type()
        if field.null and value == '':
            return None
        if field_type == FloatField.__name__:
            return float(value)
        elif "IntegerField" in field_type:
            return int(value)
        elif field_type == BooleanField.__name__:
            return bool(value)
        else:
            return str(value)

    @classmethod
    def _treat_csv(cls, file: IO[bytes], header: list[str]):
        """Get database columns and treat csv"""
        # pylint: disable=no-member
        db_fields = [f.column for f in cls._meta.fields]
        cols = parse_header_fk_names(header, cls.foreign_keys)
        cols = parse_existing_cols(cols, db_fields)
        treated_file = file
        if len(cols) != len(header):
            treated_file = filter_csv_columns(file, cols)
        return treated_file, cols

    class Meta:
        """Metadata"""
        abstract = True
