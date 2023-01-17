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


class MedianModel(models.Model):
    #TODO: Verificar filtro por trip_id -> é necessário para a predição do tempo de conclusão de um trajeto.
    # Dúvida a pedição para um ponto é também uma predicção de trajeto até esse ponto, a depender da posição no realtime?
    
    #trip_id = models.CharField(max_length=500, blank=True)
    stop_id_origin = models.CharField(max_length=500, blank=True)
    stop_id_destiny = models.CharField(max_length=500, blank=True)
    tipo_dia = models.CharField(max_length=500, blank=True)
    hora = models.CharField(max_length=500, blank=True)
