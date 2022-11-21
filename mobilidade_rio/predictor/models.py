from django.db import models

# Create your models here.
class ShapeWithStops(models.Model):
    # from trips
    trip_short_name = models.CharField(max_length=500, blank=True, null=True) # route_short_name
    
    # from stop_times
    trip_id = models.CharField(max_length=500, blank=True)
    stop_sequence = models.CharField(max_length=500, blank=True, null=True)
    stop_id = models.CharField(max_length=500, blank=True)
    shape_dist_traveled = models.CharField(max_length=500, blank=True, null=True)

    # from shapes
    shape_id = models.CharField(max_length=500, blank=True)
    shape_pt_sequence = models.CharField(max_length=500, blank=True, null=True)
    shape_pt_lat = models.CharField(max_length=500, blank=True, null=True)
    shape_pt_lon = models.CharField(max_length=500, blank=True, null=True)
    

    