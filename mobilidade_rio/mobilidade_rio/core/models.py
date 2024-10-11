import datetime
from typing import Literal
from django.conf import settings
from django.db import models
from django.utils import timezone


class TableImport(models.Model):
    """Store history of any external uploads to tables via Django"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL)
    table = models.CharField(max_length=255)
    zip_name = models.CharField(max_length=255, null=True, blank=True)
    """Name of the uploaded zip file, optional"""
    file_name = models.CharField(max_length=255, null=True, blank=True)
    """Name of the uploaded file, optional"""
    duration = models.DurationField()
    """Duration of the import process"""
    date_created = models.DateTimeField(default=timezone.now)
    """Timestamp for when the record was created"""

    @staticmethod
    def from_model(
        model: models.Model,
        user,
        duration: datetime.timedelta,
        zip_name: str,
        file_name: str,
        date_created: datetime.date = None,
    ):
        """Create new instance with typed params"""
        return TableImport(
            user=user,
            table=model._meta.db_table,
            zip_name=zip_name,
            file_name=file_name,
            duration=duration,
            date_created=date_created
        )

    def __str__(self):
        # pylint: disable=no-member
        date_created = self.date_created.strftime(r"%Y-%m-%d %H:%M:%S.%f")[:-4]
        file_path = self.get_file_path(True)
        return f"{date_created} - user '{self.user}',  file '{file_path}', to '{self.table}'"

    def get_file_path(self, spacing=False):
        """Get upload zip name and file name"""
        slash = " / " if spacing else "/"
        return f"{self.zip_name}{slash}{self.file_name}" if self.zip_name else self.file_name

    class Meta:
        """Settings for the model"""
        verbose_name = "Taple upload"
        verbose_name_plural = "Taple uploads"
        # constraints = [
        #     models.UniqueConstraint(
        #         fields=["id", "user"],
        #         name="UQ_TableUpload_id_user",
        #     )
        # ]
