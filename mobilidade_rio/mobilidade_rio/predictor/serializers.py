from mobilidade_rio.predictor.models import *
from rest_framework import serializers


class ShapeWithStopsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ShapeWithStops
        fields = "__all__"


