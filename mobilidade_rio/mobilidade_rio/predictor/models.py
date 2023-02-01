from django.db import models
from django.core.validators import MinValueValidator

# Create your models here.
class ShapesWithStops(models.Model):
    """
    Tabela shapes_with_stops
    """
    # from trips
    trip_short_name = models.CharField(max_length=500, blank=True, null=True) # route_short_name
    direction_id = models.PositiveIntegerField(blank=True, null=True)
    service_id = models.CharField(max_length=500)
    
    # from stop_times
    trip_id = models.CharField(max_length=500, blank=True)
    stop_sequence = models.PositiveIntegerField(blank=False, null=False)
    stop_id = models.CharField(max_length=500, blank=True)
    shape_dist_traveled = models.FloatField(blank=True, null=True,
        validators=[MinValueValidator(0)])

    # from shapes
    shape_id = models.CharField(max_length=500, blank=True)
    shape_pt_sequence = models.PositiveIntegerField(blank=False, null=False)
    latitude = models.FloatField(blank=False, null=False)
    longitude = models.FloatField(blank=False, null=False)

    # extra
    next_stop_id = models.CharField(max_length=500, blank=False, null=False)
    previous_stop_id = models.CharField(max_length=500, blank=False, null=False)


class Prediction(models.Model):
    """
    Contém as previsões de chegada dos veículos.

    Utiliza colunas da API realtime + colunas de predição

    Colunas
    -------
    id_veiculo
        - Para identificar o veículo em alguma trip.
        - Se a posição do veículo se alterou, o cronjob deve atualizar a previsão.
        - Retorna:
            - `None | ""`: não há veículo
            - `str`: há veículo

    dataHora
        - Nomenclatura utilizada na API realtime.
        - Data e hora da captura desses dados, \\
        para ter controle se a posição do veículo é recente ou não.

    direction_id, trip_short_name
        Para identificar a trip.

    service_id
        Variável de controle para saber se o dia da semana está correto.

    stop_id
        Quando o front fizer a requisição, ele vai passar o stop_id.
        É conveniente termos essa coluna para facilitar a consulta.

    stop_sequence
        A fim de evitar colunas duplicadas, para cada veículo, pegar o menor stop_sequence.

    arrival_time
        - Retorna:
            - `id_veiculo = (None | "")`: O tempo de chegada previsto
            entre o stop_id e o próximo stop_id.
            - `id_veiculo = str`: O tempo de chegada previsto entre o veículo e o próximo stop_id.
    """

    
    trip_id = models.CharField(max_length=500)
    stop_id = models.CharField(max_length=500)
    id_veiculo = models.CharField(max_length=500)
    latitude = models.FloatField()
    longitude = models.FloatField()
    dataHora = models.CharField(max_length=500)
    trip_short_name = models.CharField(max_length=500)
    direction_id  = models.CharField(max_length=500)
    service_id = models.CharField(max_length=500)
    arrival_time = models.CharField(max_length=500)


class MedianModel(models.Model):
    """
    Tabela que contém a mediana de tempo de viagem,
    entre dois pontos (stop), em determinada hora e dia da semana.

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
