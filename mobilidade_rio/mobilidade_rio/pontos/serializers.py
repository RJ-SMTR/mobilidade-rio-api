from mobilidade_rio.pontos.models import *
from rest_framework import serializers


class AgencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Agency
        fields = "__all__"


class CalendarSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Calendar
        fields = "__all__"


class CalendarDatesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CalendarDates
        fields = "__all__"


class RoutesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Routes
        fields = "__all__"


class TripsSerializer(serializers.HyperlinkedModelSerializer):
    route_id = RoutesSerializer()
    class Meta:
        model = Trips
        fields = "__all__"


class ShapesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shapes
        fields = "__all__"


class StopsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Stops
        fields = "__all__"


class StopTimesSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedRelatedField(view_name="stop_times-detail", read_only=True)
    trip_id = TripsSerializer(read_only=True)

    class Meta:
        model = StopTimes
        fields = ([field.name for field in StopTimes._meta.get_fields()])
        fields += ["url"]


class FrequenciesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Frequencies
        fields = "__all__"
