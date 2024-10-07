from ast import Dict, List
import datetime
import logging
from typing import IO, Any, TypedDict
from xml.dom import NotFoundErr
from zipfile import ZipFile

from django.db import IntegrityError, transaction
from rest_framework.request import Request
from rest_framework.response import Response

from mobilidade_rio.core.models import TableImport
from mobilidade_rio.utils.django_utils import is_model
from mobilidade_rio.utils.csv_utils import get_csv_header
from mobilidade_rio.utils.interfaces.base_model import BaseModel
from mobilidade_rio.pontos.models import (
    Agency,
    Calendar,
    CalendarDates,
    FareAttributes,
    FareRules,
    FeedInfo,
    Frequencies,
    Routes,
    Shapes,
    Stops,
    StopTimes,
    Trips,
)

logger = logging.getLogger("pontos_services")


class UploadGtfsDto(TypedDict):
    """Pass params to upload GTFS"""
    user: Any
    zip_name: str
    filename: str
    file: IO[bytes]
    header: list[str]


class UploadGtfsService:
    """Service to perform upload GTFS"""

    gtfs_default_names: list[str] = [
        "agency",
        "calendar_dates",
        "calendar",
        "fare_attributes",
        "fare_rules",
        "feed_info",
        "frequencies",
        "routes",
        "shapes",
        "stop_times",
        "stops",
        "trips",
    ]

    gtfs_file_order = [
        "agency.txt",
        "calendar.txt",
        "calendar_dates.txt",
        "routes.txt",
        "fare_attributes.txt",
        "fare_rules.txt",
        "feed_info.txt",
        "trips.txt",
        "frequencies.txt",
        "shapes.txt",
        "stops.txt",
        "stop_times.txt",
    ]

    gtfs_model_map: dict[str, BaseModel] = {
        "agency.txt": Agency,
        "calendar_dates.txt": CalendarDates,
        "calendar.txt": Calendar,
        "fare_attributes.txt": FareAttributes,
        "fare_rules.txt": FareRules,
        "feed_info.txt": FeedInfo,
        "frequencies.txt": Frequencies,
        "routes.txt": Routes,
        "shapes.txt": Shapes,
        "stop_times.txt": StopTimes,
        "stops.txt": Stops,
        "trips.txt": Trips,
    }

    @staticmethod
    def upload_gtfs(user, zip_file, zip_files: list[str] = None) -> Response:
        """From valid zip file, upload GTFS and return statuses"""
        try:
            start_date = datetime.datetime.now()
            uploaded = UploadGtfsService._unzip_and_upload(
                user, zip_file, zip_files)
            # pylint: disable=no-member
            TableImport.objects.bulk_create(uploaded)
            return Response({
                "uploaded": {u.table: str(u) for u in uploaded},
                "duration": datetime.datetime.now() - start_date,
                "timestamp": datetime.datetime.now(),
            }, status=200)

        except IntegrityError as e:
            return Response({
                "uploaded": None,
                "error": {
                    "type": "IntegrityError",
                    "message": str(e),
                },
                "timestamp": datetime.datetime.now(),
            }, status=200)

    @classmethod
    def _unzip_and_upload(cls, user, zip_file, zip_files: list[str] = None) -> list:
        """
        Unzip, to safe peform upload.

        If any upload fails, all uploads will rollback safely.
        """
        uploaded = []
        with ZipFile(zip_file, 'r') as zip_ref:
            filenames = cls._parse_filenames(zip_ref.namelist(), zip_files)
            for filename in filenames:
                with zip_ref.open(filename) as file:
                    header = get_csv_header(file)
                with zip_ref.open(filename) as file:
                    with transaction.atomic():
                        dto = UploadGtfsDto(user=user, zip_name=zip_file.name,
                                            filename=filename, file=file, header=header)
                        cls._find_file_and_upload(dto, uploaded)
        return uploaded

    @classmethod
    def _parse_filenames(cls, filenames: list[str], zip_files: list[str]) -> list[str]:
        """Filter by enabled models to upload and sort by dependency."""
        _filenames = filenames
        if zip_files:
            _filenames = [
                x + ".txt" for x in zip_files if x in cls.gtfs_default_names]
        new_names = cls._sort_filenames(_filenames)
        return new_names

    @classmethod
    def _sort_filenames(cls, filenames: list[str]):
        """Sort a list of names according to a predefined order."""
        order_map = {name: index
                     for index, name in enumerate(cls.gtfs_file_order)}
        sorted_names = sorted(
            filenames, key=lambda name: order_map.get(name, float('inf')))
        return sorted_names

    @classmethod
    def _find_file_and_upload(cls, dto: UploadGtfsDto, uploaded: list, error_not_found=False):
        """If file exists in expected filenames, peform upload."""
        model = cls.gtfs_model_map.get(dto["filename"], None)
        if model is None and error_not_found:
            options = ', '.join(cls.gtfs_file_order)
            raise NotFoundErr(
                f"CSV file {dto['filename']} doesnt matches the options: {options}")
        cls.upload_csv(dto, model, uploaded)

    @staticmethod
    def upload_csv(dto: UploadGtfsDto, model: BaseModel, uploaded: list):
        """Peform Upload csv file and update status"""
        start_date = datetime.datetime.now()
        # pylint: disable=protected-access
        logger.info(str(f"Importing csv for {model._meta.model_name}..."))
        model.truncate()
        if is_model(model, Stops):
            model.import_csv(dto["file"], dto["header"], orm=True)
        else:
            model.import_csv(dto["file"], dto["header"])
        upload = TableImport.from_model(
            model=model,
            date_created=datetime.datetime.now(),
            duration=datetime.datetime.now() - start_date,
            file_name=dto["filename"],
            user=dto["user"],
            zip_name=dto["zip_name"],
        )
        uploaded.append(upload)
