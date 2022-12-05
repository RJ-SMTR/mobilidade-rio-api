"""
models for GTFS data
Types are defined in the GTFS specification:
https://developers.google.com/transit/gtfs/reference
"""
from django.db import models


class Agency(models.Model):
    """Model for Agency"""
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
    service_id = models.CharField(max_length=500, blank=True, primary_key=True)
    monday = models.BooleanField(blank=True, null=True)
    tuesday = models.BooleanField(blank=True, null=True)
    wednesday = models.BooleanField(blank=True, null=True)
    thursday = models.BooleanField(blank=True, null=True)
    friday = models.BooleanField(blank=True, null=True)
    saturday = models.BooleanField(blank=True, null=True)
    sunday = models.BooleanField(blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)


class CalendarDates(models.Model):
    service_id = models.CharField(max_length=500, blank=True)
    date = models.DateField(blank=True, null=True)
    exception_type = models.IntegerField(blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['service_id', 'date'], name='calendar_date_id'
            )
        ]


class Routes(models.Model):
    route_id = models.CharField(max_length=500, blank=True, primary_key=True)
    agency_id = models.CharField(max_length=500, blank=True, null=True)
    route_short_name = models.CharField(max_length=500, blank=True, null=True)
    route_long_name = models.CharField(max_length=500, blank=True, null=True)
    route_desc = models.CharField(max_length=500, blank=True, null=True)
    route_type = models.CharField(max_length=500, blank=True, null=True)
    route_url = models.CharField(max_length=500, blank=True, null=True)
    route_branding_url = models.CharField(max_length=500, blank=True, null=True)
    route_color = models.CharField(max_length=500, blank=True, null=True)
    route_text_color = models.CharField(max_length=500, blank=True, null=True)
    route_sort_order = models.CharField(max_length=500, blank=True, null=True)
    continuous_pickup = models.CharField(max_length=500, blank=True, null=True)
    continuous_drop_off = models.CharField(max_length=500, blank=True, null=True)


class Trips(models.Model):
    trip_id = models.CharField(max_length=500, blank=True, primary_key=True)
    route_id = models.ForeignKey(Routes, on_delete=models.CASCADE, null=True)
    service_id = models.CharField(max_length=500, blank=True, null=True)
    trip_headsign = models.CharField(max_length=500, blank=True, null=True)
    trip_short_name = models.CharField(max_length=500, blank=True, null=True)
    # direction_id = models.IntegerField(blank=True, null=True)
    direction_id = models.CharField(max_length=500, blank=True, null=True)  # TODO: change to int
    block_id = models.CharField(max_length=500, blank=True, null=True)
    shape_id = models.CharField(max_length=500, blank=True, null=True)
    wheelchair_accessible = models.CharField(max_length=500, blank=True, null=True)
    bikes_allowed = models.CharField(max_length=500, blank=True, null=True)


class Shapes(models.Model):
    shape_id = models.CharField(max_length=500, blank=True)
    shape_pt_sequence = models.CharField(max_length=500, blank=True, null=True)
    shape_pt_lat = models.CharField(max_length=500, blank=True, null=True)
    shape_pt_lon = models.CharField(max_length=500, blank=True, null=True)
    shape_dist_traveled = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['shape_id', 'shape_pt_sequence'], name='shape_sequence_id'
            )
        ]


class Stops(models.Model):
    stop_id = models.CharField(max_length=500, blank=True, primary_key=True)
    stop_code = models.CharField(max_length=500, blank=True, null=True)
    stop_name = models.CharField(max_length=500, blank=True, null=True)
    stop_desc = models.CharField(max_length=500, blank=True, null=True)
    stop_lat = models.CharField(max_length=500, blank=True, null=True)
    stop_lon = models.CharField(max_length=500, blank=True, null=True)
    zone_id = models.CharField(max_length=500, blank=True, null=True)
    stop_url = models.CharField(max_length=500, blank=True, null=True)
    location_type = models.CharField(max_length=500, blank=True, null=True)
    parent_station = models.CharField(max_length=500, blank=True, null=True)
    stop_timezone = models.CharField(max_length=500, blank=True, null=True)
    wheelchair_boarding = models.CharField(max_length=500, blank=True, null=True)
    platform_code = models.CharField(max_length=500, blank=True, null=True)


class StopTimes(models.Model):
    trip_id = models.ForeignKey(Trips, on_delete=models.CASCADE, related_name='trip_id_id', related_query_name='trip_id_id')
    # trip_id = models.CharField(max_length=500, blank=True)
    stop_sequence = models.CharField(max_length=500, blank=True, null=True)
    stop_id = models.CharField(max_length=500, blank=True)
    arrival_time = models.CharField(max_length=500, blank=True, null=True)
    departure_time = models.CharField(max_length=500, blank=True, null=True)
    stop_headsign = models.CharField(max_length=500, blank=True, null=True)
    pickup_type = models.CharField(max_length=500, blank=True, null=True)
    drop_off_type = models.CharField(max_length=500, blank=True, null=True)
    continuous_pickup = models.CharField(max_length=500, blank=True, null=True)
    continuous_drop_off = models.CharField(max_length=500, blank=True, null=True)
    shape_dist_traveled = models.CharField(max_length=500, blank=True, null=True)
    timepoint = models.CharField(max_length=500, blank=True, null=True)

    # TODO: check constraint for circular routes
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['trip_id', 'stop_id'], name='stop_times_id'
    #         )
    #     ]


class Frequencies(models.Model):
    trip_id = models.CharField(max_length=500, blank=True)
    start_time = models.CharField(max_length=500, blank=True, null=True)
    end_time = models.CharField(max_length=500, blank=True, null=True)
    headway_secs = models.CharField(max_length=500, blank=True, null=True)
    exact_times = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['trip_id', 'start_time'], name='frequency_id'
            )
        ]
