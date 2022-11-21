#from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from mobilidade_rio.predictor.models import *
from mobilidade_rio.predictor.serializers import *

class ShapeWithStopsViewSet(viewsets.ModelViewSet):
    serializer_class = ShapeWithStopsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ShapeWithStops.objects.all().order_by("trip_id")
    '''
    def get_queryset(self):
        queryset = ShapeWithStops.objects.all().order_by("trip_id")
        stop_id = None
        # get stop_id from query params
        if 'stop_id' in self.request.query_params:
            stop_id = self.request.query_params.get('stop_id')

        if stop_id is not None:
            # get multiple stop_ids
            stop_ids = stop_id.split(",")
            stops = queryset.filter(stop_id__in=stop_ids)

            # If some stop_id from input is not in results, return empty
            stop_id_list = stops.order_by("stop_id").values_list('stop_id', flat=True).distinct()
            if len(stop_id_list) != len(stop_ids):
                return queryset.none()
            """
            # filter if trips passing by all stop_ids
            trip_id_list = stops.order_by('trip_id').values_list('trip_id', flat=True).distinct()
            trip_id_list = [str(trip_id) for trip_id in trip_id_list]
            stops = stops.filter(trip_id__in=trip_id_list)

            # filter if trips passing by all stop_ids
            stop_id_queries = [stops.filter(stop_id=_stop_id) for _stop_id in stop_ids]
            for trip_id in list(trip_id_list):
                for stop_query in stop_id_queries:
                    query = stop_query.filter(trip_id=trip_id)
                    if not query:
                        trip_id_list.remove(trip_id)
                        break
            

            queryset = stops.filter(trip_id__in=trip_id_list)
            """

            # order by
            queryset = queryset.order_by("trip_id", "stop_sequence")

        return queryset
    '''
class PredictorViewSet(viewsets.ModelViewSet):
    pass