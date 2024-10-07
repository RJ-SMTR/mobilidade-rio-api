from django.db import models

def is_model(model: models.Model, *compare_models: models.Model):
    """Compare two Django models"""
    for compare_model in compare_models:
        # pylint: disable=protected-access
        if model._meta.label != compare_model._meta.label:
            return False
    return True

