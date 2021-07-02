from django.db import models


class Ponto (models.Model):
    identifier = models.CharField(max_length=10)
    address = models.CharField(max_length=150)
    latitude = models.FloatField()
    longitude = models.FloatField()

    def __str__(self):
        return f"Ponto {self.identifier}: {self.address}"


class QrCode (models.Model):
    identifier = models.CharField(max_length=4)
    ponto = models.OneToOneField(
        Ponto, on_delete=models.CASCADE, primary_key=True)

    def __str__(self):
        return f"QrCode {self.identifier}: {self.ponto}"
