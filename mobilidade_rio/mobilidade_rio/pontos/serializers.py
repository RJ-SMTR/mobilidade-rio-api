from .models import Mode, Stop, QrCode, Linha, Agency, Route, Trip, Sequence
from rest_framework import serializers


class ModeSerializer (serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Mode
        fields = ('url', 'id', 'name')


class StopSerializer (serializers.HyperlinkedModelSerializer):
    mode = ModeSerializer()

    class Meta:
        model = Stop
        fields = ('url', 'id', 'name', 'address',
                  'latitude', 'longitude', 'mode')


class QrCodeSerializer (serializers.HyperlinkedModelSerializer):
    stop = StopSerializer()

    class Meta:
        model = QrCode
        fields = ('url', 'code', 'stop')


class AgencySerializer (serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Agency
        fields = ('url', 'id', 'name')


class LinhaSerializer (serializers.HyperlinkedModelSerializer):
    mode = ModeSerializer()
    agency = AgencySerializer()

    class Meta:
        model = Linha
        fields = ('url', 'id', 'initials', 'mode', 'agency')


class RouteSerializer (serializers.HyperlinkedModelSerializer):
    linha = LinhaSerializer()
    agency = AgencySerializer()
    mode = ModeSerializer()

    class Meta:
        model = Route
        fields = ('url', 'id', 'linha', 'agency',
                  'mode', 'short_name', 'vista')


class TripSerializer (serializers.HyperlinkedModelSerializer):
    route = RouteSerializer()

    class Meta:
        model = Trip
        fields = ('url', 'id', 'route', 'headsign',
                  'via', 'version', 'direction')


class SequenceSerializer (serializers.HyperlinkedModelSerializer):
    trip = TripSerializer()
    stop = StopSerializer()

    class Meta:
        model = Sequence
        fields = ('url', 'id', 'trip', 'stop', 'order')
