from django.conf import settings
from django.core.files.storage import default_storage


def remove_file_if_exists(filename:str):
    """Remove Django media file if exists, using relative Django filename only"""
    if default_storage.exists(filename):
        path = f"{settings.MEDIA_ROOT}/{filename}"
        default_storage.delete(path)
