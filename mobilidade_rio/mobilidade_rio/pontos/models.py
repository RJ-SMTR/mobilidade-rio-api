from django.db import models


class Agency (models.Model):
    agency_id = models.IntegerField(primary_key=True)
    agency_name= models.CharField(max_length=50)
    
    def __str__(self):
        return f"Agência {self.agency_name}"


class Route (models.Model):
    route_id = models.CharField(max_length=50, primary_key=True)
    agency_id = models.ForeignKey(Agency, on_delete=models.CASCADE)
    route_type = models.IntegerField(default=3)
    route_short_name = models.CharField(max_length=50)
    route_long_name = models.CharField(max_length=150, default="")

    def __str__(self):
        return f"Rota {self.route_id} - {self.route_short_name}"

class Trip (models.Model):  
    trip_id = models.CharField(max_length=50, primary_key=True)
    route_id = models.ForeignKey(Route, on_delete=models.CASCADE)
    trip_headsign = models.CharField(max_length=250)
    direction_id = models.IntegerField(default=0)

    def __str__(self):
        return f"Viagem {self.route_id} - {self.trip_headsign}"


class Stop (models.Model):
    stop_id = models.CharField(max_length=50, primary_key=True)
    stop_name = models.CharField(max_length=250)
    stop_lat = models.FloatField(null=True)
    stop_lon = models.FloatField(null=True)

    def __str__(self):
        return f"Ponto {self.stop_name}"


class QrCode (models.Model):
    stop_code = models.CharField(max_length=4)
    stop_id = models.OneToOneField(
        Stop, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"QrCode {self.stop_code}: {self.stop_id}"

class Stop_times (models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    trip_id = models.ForeignKey(Trip, on_delete=models.CASCADE)
    stop_id = models.ForeignKey(Stop, on_delete=models.CASCADE)
    stop_sequence = models.IntegerField()

    def __str__(self):
        return f"Sequência {self.trip_id} - {self.stop_id} - {self.order}"