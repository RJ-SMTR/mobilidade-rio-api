"""
django_utils.py
General functions and helpers for Django.
Query helpersusing Django ORM and raw SQL queries.
"""

from django.db import connection

def get_table(model):
    """Get real table name from model"""
    return model._meta.db_table

def get_col(model, col):
    """Get real column name from model"""
    return model._meta.get_field(col).column

def postgis_exists() -> bool:
    """Check if postgis extension is enabled"""
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1 FROM pg_extension WHERE extname = 'postgis'")
        return cursor.fetchone() is not None
