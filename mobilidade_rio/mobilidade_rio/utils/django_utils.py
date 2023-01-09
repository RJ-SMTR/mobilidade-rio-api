"""
django_utils.py
General functions and helpers for Django.
Query helpersusing Django ORM and raw SQL queries.
"""

def get_table(model):
    """Get real table name from model"""
    return model._meta.db_table

def get_col(model, col):
    """Get real column name from model"""
    return model._meta.get_field(col).column
