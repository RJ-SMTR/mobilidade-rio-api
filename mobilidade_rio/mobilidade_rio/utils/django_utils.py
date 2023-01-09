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

def get_cols(models, exclude=[]):
    """Get all real column names from model"""
    # add cols for all models
    if isinstance(models,(list, tuple)):
        ret = []
        for model in models:
            print("model", type(model))
            print("ret", type(ret))
            ret += get_cols(model)
        # treat list
        ret = list(dict.fromkeys(ret))
        ret = [c for c in ret if c not in exclude]
        return ret
    # add all cols from model
    else:
        ret = [c.name for c in models._meta.get_fields()]
        ret = [c for c in ret if c not in exclude]
        return ret
