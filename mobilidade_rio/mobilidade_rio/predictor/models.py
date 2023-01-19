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


class Prediction(models.Model):
    """
    Contém colunas da API realtime + colunas de predição

    É a tabela que vai guardar as previsões de chegada dos veículos.

    Colunas
    -------
    id_veiculo
        Para saber se posição do veículo se alterou, para atualizar o banco.

    data_hora
        Pra ter controle se a posição do veículo é recente ou não.

    direction_id, trip_short_name
        Para identificar a trip.

    service_id
        Variável de controle para saber se o dia da semana está correto.

    stop_id
        Quando o front fizer a requisição, ele vai passar o stop_id.
        É conveniente termos essa coluna para facilitar a consulta.

    stop_sequence
        A fim de evitar colunas duplicadas, para cada veículo, pegar o menor stop_sequence.
    """

    # API realtime
    
    # são relacionados com o mesmo stop_id
    id_veiculo = models.CharField(max_length=500)
    latitude = models.FloatField()
    longitude = models.FloatField()
    data_hora = models.CharField(max_length=500)
    trip_short_name = models.CharField(max_length=500)
    direction_id  = models.CharField(max_length=500)
    service_id = models.CharField(max_length=500)
    stop_sequence = models.IntegerField()
    stop_id = models.CharField(max_length=500)
    arrival_time = models.IntegerField()

# ArrayField(models.CharField(max_length=500), blank=True, null=True)


class MedianModel(models.Model):
    """
    Porcentagem ...

    Colunas
    -------

    tipo_dia (weekday)
    stop_id_origin
    stop_id_destiny
    """
    stop_id_origin = models.CharField(max_length=500, blank=True)
    stop_id_destiny = models.CharField(max_length=500, blank=True)
    tipo_dia = models.CharField(max_length=500, blank=True)
    hora = models.IntegerField()
    delta_secs = models.FloatField()
