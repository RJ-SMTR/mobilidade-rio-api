from .models import Ponto, QrCode
from rest_framework import serializers


class PontoSerializer (serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Ponto
        fields = ["url", "identifier", "address", "latitude", "longitude"]


class QrCodeSerializer (serializers.HyperlinkedModelSerializer):
    ponto = PontoSerializer()

    class Meta:
        model = QrCode
        fields = ["url", "identifier", "ponto"]
