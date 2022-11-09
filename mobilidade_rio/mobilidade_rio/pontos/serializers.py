from mobilidade_rio.pontos.models import Agency, Route, Stop, QrCode, Trip, Stop_times
from rest_framework import serializers

class StopSerializer (serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = Stop
        fields = ('url', 'stop_id', 'stop_name', 'stop_lat',
                  'stop_lat', 'stop_lon')

#troquei stop_id por stop add stopserializaer
class QrCodeSerializer (serializers.HyperlinkedModelSerializer):
    stop_id = StopSerializer(read_only=True)

    class Meta:
        model = QrCode
        fields = ('url', 'stop_code', 'stop_id')
        

class AgencySerializer (serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Agency
        fields = ('url', 'agency_id', 'agency_name')


class RouteSerializer (serializers.HyperlinkedModelSerializer):
    agency_id = AgencySerializer(read_only=True)
    
    
    class Meta:
        model = Route
        fields = ('url', 'route_id', 'agency_id',
                  'route_type', 'route_short_name', 'route_long_name')


class TripSerializer (serializers.HyperlinkedModelSerializer):
    route_id = RouteSerializer(read_only=True)

    class Meta:
        model = Trip
        fields = ('url', 'trip_id', 'route_id', 'trip_headsign', 'direction_id')


class SequenceSerializer (serializers.HyperlinkedModelSerializer):
    trip_id = TripSerializer(read_only=True)
    stop_id = StopSerializer(read_only=True)

    class Meta:
        model = Stop_times
        fields = ('url', 'trip_id', 'stop_id', 'order')
