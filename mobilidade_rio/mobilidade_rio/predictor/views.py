from rest_framework import viewsets
from rest_framework import permissions
from mobilidade_rio.predictor.models import *
from mobilidade_rio.pontos.models import *
from mobilidade_rio.predictor.serializers import *
import mobilidade_rio.utils.query_utils as qu
import mobilidade_rio.predictor.utils as utils

class ShapesWithStopsViewSet(viewsets.ModelViewSet):
    serializer_class = ShapeWithStopsSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
    queryset = ShapesWithStops.objects.all().order_by("trip_id")

    def get_queryset(self):
        queryset = ShapesWithStops.objects.all().order_by("trip_id")
        query = queryset.query.__str__()

        # filter by stop_id (shapes with stops)
        stop_id = self.request.query_params.get('stop_id')
        if stop_id is not None:
            stop_id = stop_id.split(",")
            query = utils.q_shapes_with_stops(stop_id=stop_id)

        # get route_type
        route_type = self.request.query_params.get('route_type')
        if route_type is not None:
            route_type = route_type.split(",")
            routes = f"""
                SELECT route_id FROM pontos_routes
                WHERE route_type IN ({','.join(route_type)})
            """
            query = f"""
                SELECT * FROM ({query}) AS {qu.q_random_hash("q_shapes_stoptimes")}
                WHERE route_id IN ({routes})
            """

        # execute query
        queryset = queryset.raw(query)

        return queryset
