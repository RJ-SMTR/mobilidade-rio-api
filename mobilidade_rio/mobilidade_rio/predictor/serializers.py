from mobilidade_rio.predictor.models import *
from rest_framework import serializers


class ShapeWithStopsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShapesWithStops
        fields = "__all__"
