from django.db import models


class Mode (models.Model):
    name = models.CharField(max_length=30)

    def __str__(self):
        return f"Modo {self.name}"


class Stop (models.Model):
    mode = models.ForeignKey(Mode, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=150)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"Ponto {self.name}: {self.address}"


class QrCode (models.Model):
    code = models.CharField(max_length=4)
    stop = models.OneToOneField(
        Stop, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"QrCode {self.code}: {self.stop}"


class Linha (models.Model):
    initials = models.CharField(max_length=10)

    def __str__(self):
        return f"Linha {self.initials}"


class Agency (models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"Agência {self.name}"


class Route (models.Model):
    linha = models.ForeignKey(Linha, on_delete=models.CASCADE)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    mode = models.ForeignKey(Mode, on_delete=models.CASCADE)
    short_name = models.CharField(max_length=50)

    def __str__(self):
        return f"Rota {self.linha} - {self.short_name}"


class Trip (models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    headsign = models.CharField(max_length=50)
    via = models.CharField(max_length=50, blank=True)
    version = models.CharField(max_length=50)

    def __str__(self):
        return f"Viagem {self.route} - {self.headsign}"


class Sequence (models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    order = models.IntegerField()

    def __str__(self):
        return f"Sequência {self.trip} - {self.stop} - {self.order}"
