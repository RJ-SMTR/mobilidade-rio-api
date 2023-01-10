from mobilidade_rio.predictor.models import *
from rest_framework import serializers


class ShapesWithStopsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShapesWithStops
        fields = "__all__"
