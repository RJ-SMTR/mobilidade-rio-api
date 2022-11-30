from mobilidade_rio.pontos.models import *
from rest_framework import serializers


class AgencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Agency
        fields = [field.name for field in model._meta.fields]


class CalendarSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Calendar
        fields = [field.name for field in model._meta.fields]


class CalendarDatesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CalendarDates
        fields = [field.name for field in model._meta.fields]


class RoutesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Routes
        fields = [field.name for field in model._meta.fields]


class TripsSerializer(serializers.HyperlinkedModelSerializer):
    route_id = RoutesSerializer()
    class Meta:
        model = Trips
        fields = [field.name for field in model._meta.fields]


class ShapesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shapes
        fields = [field.name for field in model._meta.fields]


class StopsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Stops
        fields = [field.name for field in model._meta.fields]


class StopTimesSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedRelatedField(view_name="stop_times-detail", read_only=True)
    trip_id = TripsSerializer(read_only=True)

    class Meta:
        model = StopTimes
        fields = [field.name for field in model._meta.fields]
        fields.append("url")


class FrequenciesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Frequencies
        fields = [field.name for field in model._meta.fields]
