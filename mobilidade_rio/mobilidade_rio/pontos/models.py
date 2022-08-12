from django.db import models


class Mode (models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=30)

    def __str__(self):
        return f"Modo {self.name}"


class Stop (models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    mode = models.ForeignKey(Mode, on_delete=models.CASCADE, null=True)
    name = models.CharField(max_length=250)
    address = models.CharField(max_length=250, null=True)
    latitude = models.FloatField(null=True)
    longitude = models.FloatField(null=True)

    def __str__(self):
        return f"Ponto {self.name}: {self.address}"


class QrCode (models.Model):
    code = models.CharField(max_length=10)
    stop = models.OneToOneField(
        Stop, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"QrCode {self.code}: {self.stop}"


class Agency (models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"Agência {self.name}"


class Linha (models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE, null=True)
    mode = models.ForeignKey(Mode, on_delete=models.CASCADE, null=True)
    initials = models.CharField(max_length=10)
    name = models.CharField(max_length=150, default="")

    def __str__(self):
        return f"Linha {self.initials}"


class Route (models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    linha = models.ForeignKey(Linha, on_delete=models.CASCADE)
    agency = models.ForeignKey(Agency, on_delete=models.CASCADE)
    mode = models.ForeignKey(Mode, on_delete=models.CASCADE)
    short_name = models.CharField(max_length=50)
    vista = models.CharField(max_length=150, default="")

    def __str__(self):
        return f"Rota {self.linha} - {self.short_name}"


class Trip (models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE)
    headsign = models.CharField(max_length=250)
    via = models.CharField(max_length=50, blank=True, null=True)
    version = models.CharField(max_length=50, blank=True, null=True)
    direction = models.IntegerField(default=0)

    def __str__(self):
        return f"Viagem {self.route} - {self.headsign}"


class Sequence (models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE)
    stop = models.ForeignKey(Stop, on_delete=models.CASCADE)
    order = models.IntegerField()

    def __str__(self):
        return f"Sequência {self.trip} - {self.stop} - {self.order}"
