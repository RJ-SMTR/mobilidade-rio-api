"""
models for GTFS data
Types are defined in the GTFS specification:
https://developers.google.com/transit/gtfs/reference
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q


class Agency(models.Model):
    """
    Model for agency.txt
    Mandatory fields: agency_id, agency_name, agency_url, agency_timezone
    """

    agency_id = models.CharField(max_length=500, blank=True, primary_key=True)
    agency_name = models.CharField(max_length=500, blank=False, null=False)
    agency_url = models.URLField(max_length=500, blank=False, null=False)
    agency_timezone = models.CharField(max_length=500, blank=False, null=False)
    agency_lang = models.CharField(max_length=500, blank=True, null=True)
    agency_phone = models.CharField(max_length=500, blank=True, null=True)
    agency_branding_url = models.CharField(max_length=500, blank=True, null=True)
    agency_fare_url = models.CharField(max_length=500, blank=True, null=True)
    agency_email = models.CharField(max_length=500, blank=True, null=True)


class Calendar(models.Model):
    """
    Model for calendar.txt
    Mandatory fields: all
    """

    service_id = models.CharField(max_length=500, blank=True, primary_key=True)
    monday = models.IntegerField(blank=False, null=False)
    tuesday = models.IntegerField(blank=False, null=False)
    wednesday = models.IntegerField(blank=False, null=False)
    thursday = models.IntegerField(blank=False, null=False)
    friday = models.IntegerField(blank=False, null=False)
    saturday = models.IntegerField(blank=False, null=False)
    sunday = models.IntegerField(blank=False, null=False)
    start_date = models.DateField(blank=False, null=False)
    end_date = models.DateField(blank=False, null=False)


class CalendarDates(models.Model):
    """
    Model for calendar_dates.txt
    Mandatory fields: service_id, date, exception_type
    """

    service_id = models.CharField(max_length=500, blank=False, null=False)
    date = models.DateField(blank=False, null=False)
    # TODO: change to real ENUM type in database
    exception_type = models.CharField(
        max_length=500,
        blank=False,
        null=False,
        choices=(("1", "Added service"), ("2", "Removed service")),
    )

    class Meta:
        """Constraints for the model"""

        constraints = [
            models.UniqueConstraint(
                fields=["service_id", "date"], name="calendar_date_id"
            )
        ]


class Routes(models.Model):
    """
    Model for routes.txt
    Mandatory fields:
        route_id, agency_id, route_short_name, route_long_name, route_type
    Primary keys: route_id, agency_id
    Foreign keys: agency_id
    Non GTFS fields: route_branding_url
    """

    route_id = models.CharField(max_length=500, blank=False, primary_key=True)
    agency_id = models.ForeignKey(
        Agency, on_delete=models.CASCADE, blank=False, null=False
    )
    route_short_name = models.CharField(max_length=500, blank=False, null=False)
    route_long_name = models.CharField(max_length=500, blank=False, null=False)
    route_desc = models.CharField(max_length=500, blank=True, null=True)
    route_type = models.IntegerField(
        blank=False,
        null=False,
        choices=(
            (0, "VLT"),
            (1, "Urban trains and subways"),
            (2, "Interurban trains and subways"),
            (3, "Bus"),
            (4, "Ferry"),
            (5, "Cable car"),
            (6, "Gondola"),
            (7, "Funicular"),
            (11, "Tram"),
            (12, "Monorail"),
        ),
    )
    route_url = models.URLField(max_length=500, blank=True, null=True)
    route_branding_url = models.URLField(max_length=500, blank=True, null=True)
    route_color = models.CharField(max_length=500, blank=True, null=True)
    route_text_color = models.CharField(max_length=500, blank=True, null=True)
    route_sort_order = models.PositiveIntegerField(blank=True, null=True)
    continuous_pickup = models.IntegerField(
        blank=True,
        null=True,
        choices=(
            (0, "embarking with continuous stops"),
            (1, "no embarking available"),
            (2, "set embarking with the company"),
            (3, "set embarking with the driver"),
        ),
    )
    continuous_drop_off = models.IntegerField(
        blank=True,
        null=True,
        default=1,
        choices=(
            (0, "disembarking with continuous stops"),
            (1, "no disembarking available"),
            (2, "set disembarking with the company"),
            (3, "set disembarking with the driver"),
        ),
    )


class Trips(models.Model):
    """
    Model for trips.txt
    Mandatory fields:
        route_id,
        service_id,
        shape_id: under certain conditions (see GTFS reference)
    Primary keys: trip_id, block_id
    Foreign keys: route_id, shape_id
    """

    route_id = models.ForeignKey(Routes, on_delete=models.CASCADE, null=True)
    service_id = models.CharField(max_length=500, blank=False, null=False)
    trip_id = models.CharField(max_length=500, blank=True, primary_key=True)
    trip_headsign = models.CharField(max_length=500, blank=True, null=True)
    trip_short_name = models.CharField(max_length=500, blank=True, null=True)
    direction_id = models.IntegerField(
        blank=True, null=True, choices=((0, "ida"), (1, "volta"))
    )
    block_id = models.CharField(max_length=500, blank=True, null=True)
    shape_id = models.CharField(max_length=500, blank=True, null=True)
    wheelchair_accessible = models.IntegerField(
        blank=True,
        null=True,
        choices=(
            (0, "information not available"),
            (1, "accessible"),
            (2, "not accessible"),
        ),
    )
    bikes_allowed = models.IntegerField(
        blank=True,
        null=True,
        choices=((0, "information not available"), (1, "allowed"), (2, "not allowed")),
    )

    class Meta:
        """Constraints for the model"""

        constraints = [
            models.UniqueConstraint(
                # treat block_id as another primary key
                fields=["trip_id", "block_id"],
                name="trip_block_id",
            )
        ]


class Shapes(models.Model):
    """
    Model for shapes.txt
    Mandatory fields: shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence
    Primary keys: shape_id + shape_pt_sequence
    """

    shape_id = models.CharField(max_length=500, blank=False, null=False)
    shape_pt_lat = models.FloatField(blank=False, null=False)
    shape_pt_lon = models.FloatField(blank=False, null=False)
    shape_pt_sequence = models.PositiveIntegerField(blank=False, null=False)
    shape_dist_traveled = models.FloatField(
        blank=True, null=True, validators=[MinValueValidator(0)]
    )

    class Meta:
        """Constraints for the model"""

        constraints = [
            models.UniqueConstraint(
                # composite primary key
                fields=["shape_id", "shape_pt_sequence"],
                name="shape_sequence_id",
            )
        ]


class Stops(models.Model):
    """
    Model for stops.txt

    Mandatory fields:
        stop_id,
        stop_name: mandatory when name is comprehensive
            e.g. "Rio de Janeiro" instead of "RJ" (TODO)
        stop_lat, stop_lon : mandatory when local_type is 0, 1 or 2,
        zone_id: mandatory if fare information is provided via fare_rules.txt (TODO)
        parent_station:
            mandatory if location_type is 2, 3, 4
            forbidden if location_type is 1 (station, stop parent)
            optional if location_type is 0, None (platform, stop child)


    Primary keys: stop_id
    Foreign keys: parent_station,
        zone_id, level_id (TODO)
    """

    stop_id = models.CharField(max_length=500, blank=False, primary_key=True)
    stop_code = models.CharField(max_length=500, blank=True, null=True)
    stop_name = models.CharField(max_length=500, blank=True, null=True)
    stop_desc = models.CharField(max_length=500, blank=True, null=True)
    stop_lat = models.FloatField(blank=True, null=True)
    stop_lon = models.FloatField(blank=True, null=True)
    zone_id = models.CharField(max_length=500, blank=True, null=True)
    stop_url = models.URLField(max_length=500, blank=True, null=True)
    location_type = models.IntegerField(
        blank=True,
        null=True,
        choices=(
            (0, "stop"),
            (1, "station"),
            (2, "entrance/exit"),
            (3, "generic node"),
            (4, "boarding area"),
        ),
    )
    parent_station = models.ForeignKey(
        "self", on_delete=models.CASCADE, blank=True, null=True
    )
    stop_timezone = models.CharField(max_length=500, blank=True, null=True)
    wheelchair_boarding = models.IntegerField(
        blank=True,
        null=True,
        choices=(
            (0, "information not available"),
            (1, "available"),
            (2, "not available"),
        ),
    )
    level_id = models.CharField(max_length=500, blank=True, null=True)
    platform_code = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        """Constraints for the model"""

        constraints = [
            # stop_lat and stop_lon are mandatory when location_type is 0, 1 or 2
            models.CheckConstraint(
                check=~Q(location_type__in=[0, 1, 2])
                | Q(stop_lat__isnull=False) & Q(stop_lon__isnull=False),
                name="stop_lat_lon",
            ),
            models.CheckConstraint(
                # parent_station is mandatory if location_type is 2, 3, 4
                check=~Q(location_type__in=[2, 3, 4]) | Q(parent_station__isnull=False),
                name="parent_station_mandatory",
            ),
            # parent_station is forbidden if location_type is 1
            models.CheckConstraint(
                check=~Q(location_type=1) | Q(parent_station__isnull=True),
                name="parent_station_forbidden",
            ),
            # treat stop_code as another primary key
            models.UniqueConstraint(
                fields=["stop_id", "stop_code"], name="stop_code_id"
            ),
        ]


class StopTimes(models.Model):
    """
    Model for stop_times.txt
    Mandatory fields: trip_id, stop_id, stop_sequence
        arrival_time: mandatory if stop is the first or last stop of a trip (TODO)
        stop_id, stop_sequence
    Optional fields: departure_time: mandatory "if you can insert it", so it's optional
    Primary keys: trip_id + stop_sequence + stop_id
    Foreign keys: trip_id, stop_id
    """

    trip_id = models.ForeignKey(
        Trips,
        on_delete=models.CASCADE,
        related_name="trip_id_id",
        related_query_name="trip_id_id",
    )
    stop_sequence = models.PositiveIntegerField(blank=False, null=False)
    stop_id = models.ForeignKey(
        Stops,
        on_delete=models.CASCADE,
        related_name="stop_id_id",
        related_query_name="stop_id_id",
    )
    arrival_time = models.CharField(blank=True, null=True, max_length=10)
    departure_time = models.CharField(blank=True, null=True, max_length=10)
    stop_headsign = models.CharField(max_length=500, blank=True, null=True)
    pickup_type = models.IntegerField(
        blank=True,
        null=True,
        default=1,
        choices=(
            (0, "regularly scheduled embarking"),
            (1, "no embarking available"),
            (2, "set embarking with the company"),
            (3, "set embarking with the driver"),
        ),
    )
    drop_off_type = models.IntegerField(
        blank=True,
        null=True,
        default=1,
        choices=(
            (0, "regularly scheduled disembarking"),
            (1, "no disembarking available"),
            (2, "set disembarking with the company"),
            (3, "set disembarking with the driver"),
        ),
    )
    continuous_pickup = models.IntegerField(
        blank=True,
        null=True,
        choices=(
            (0, "embarking with continuous stops"),
            (1, "no embarking available"),
            (2, "set embarking with the company"),
            (3, "set embarking with the driver"),
        ),
    )
    continuous_drop_off = models.IntegerField(
        blank=True,
        null=True,
        default=1,
        choices=(
            (0, "disembarking with continuous stops"),
            (1, "no disembarking available"),
            (2, "set disembarking with the company"),
            (3, "set disembarking with the driver"),
        ),
    )
    shape_dist_traveled = models.FloatField(
        max_length=500, blank=True, null=True, validators=[MinValueValidator(0)]
    )
    timepoint = models.IntegerField(
        blank=True, null=True, choices=((0, "exact time"), (1, "approximate time"))
    )

    class Meta:
        """Constraints for the model"""

        # composite primary key: trip_id + stop_sequence + stop_id
        constraints = [
            # TODO: For testing purposes, this composite primary key is disabled
            # ?   because of errors like "Key (trip_id_id, stop_id_id, stop_sequence)
            # ?       =(O0108AAA0AIDU01, 1003O00022P0, 35) already exists."
            # models.UniqueConstraint(
            #     fields=['trip_id', 'stop_id', 'stop_sequence'], name='trip_stop_sequence'
            # )
        ]


class Frequencies(models.Model):
    """
    Model for frequencies.txt
    Mandatory fields: trip_id, start_time, end_time, headway_secs
    Primary keys: trip_id + start_time
    Foreign keys: trip_id
    """

    trip_id = models.ForeignKey(
        Trips, on_delete=models.CASCADE, blank=False, null=False
    )
    # ? `start_time` and `end_time` can exceed 23:59:59, so they are stored as Char
    start_time = models.CharField(blank=False, null=False, max_length=10)
    end_time = models.CharField(blank=False, null=False, max_length=10)
    headway_secs = models.PositiveIntegerField(blank=False, null=False)
    exact_times = models.IntegerField(
        blank=True,
        null=True,
        choices=((0, "frequency-based trips"), (1, "exact times")),
    )

    class Meta:
        """Constraints for the model"""

        constraints = [
            models.UniqueConstraint(
                fields=["trip_id", "start_time"], name="frequency_id"
            ),
            # if start_time and end_time are hh:mm:ss
            models.CheckConstraint(
                check=Q(start_time__regex=r"^[0-9]+:[0-9]{1,2}:[0-9]{1,2}$"),
                name="start_time_format",
            ),
            models.CheckConstraint(
                check=Q(end_time__regex=r"^[0-9]+:[0-9]{1,2}:[0-9]{1,2}$"),
                name="end_time_format",
            ),
        ]
