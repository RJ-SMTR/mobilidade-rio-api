from django.db import models

# Create your models here.
class ShapesWithStops(models.Model):

    # stop_times
    trip_id = models.CharField(max_length=500, blank=True, null=True)
    stop_sequence = models.CharField(max_length=500, blank=True, null=True)
    stop_id = models.CharField(max_length=500, blank=True, null=True)
    arrival_time = models.CharField(max_length=500, blank=True, null=True)
    departure_time = models.CharField(max_length=500, blank=True, null=True)
    pickup_type = models.CharField(max_length=500, blank=True, null=True)
    drop_off_type = models.CharField(max_length=500, blank=True, null=True)

    # shapes
    shape_id = models.CharField(max_length=500, blank=True, null=True)
    shape_dist_traveled = models.CharField(max_length=500, blank=True, null=True)
    shape_pt_sequence = models.CharField(max_length=500, blank=True, null=True)
    shape_pt_lat = models.CharField(max_length=500, blank=True, null=True)
    shape_pt_lon = models.CharField(max_length=500, blank=True, null=True)

    # stops
    stop_id = models.CharField(max_length=500, blank=True, null=True)
    stop_name = models.CharField(max_length=500, blank=True, null=True)
    stop_lat = models.CharField(max_length=500, blank=True, null=True)
    stop_lon = models.CharField(max_length=500, blank=True, null=True)
    stop_code = models.CharField(max_length=500, blank=True, null=True)
    stop_desc = models.CharField(max_length=500, blank=True, null=True)
    zone_id = models.CharField(max_length=500, blank=True, null=True)
    stop_url = models.CharField(max_length=500, blank=True, null=True)
    stop_timezone = models.CharField(max_length=500, blank=True, null=True)
    wheelchair_boarding = models.CharField(max_length=500, blank=True, null=True)

    # trips
    trip_short_name = models.CharField(max_length=500, blank=True, null=True) # route_short_name
    trip_id = models.CharField(max_length=500, blank=True, null=True)

    # routes
    route_id = models.CharField(max_length=500, blank=True, null=True)
    route_short_name = models.CharField(max_length=500, blank=True, null=True)
    route_long_name = models.CharField(max_length=500, blank=True, null=True)
