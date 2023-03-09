#from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.response import Response
from mobilidade_rio.predictor.models import *
from mobilidade_rio.predictor.serializers import *
from mobilidade_rio.predictor.utils import *


class PredictorViewSet(viewsets.ViewSet):
    """
    A viewset that returns JSON data as if it's a model.
    """
    _="""
    # TODO: add pagination or use a real ModelViewSet
    """

    def list(self, request):
        """
        Return a JSON representation of the data.
        """

        ret = []

        # stop_code
        stop_code = self.request.query_params.get("stop_code")
        if stop_code:
            pred = Predictor([],[],[])
            # print(pred)
            # pred.get_eta()
            ret = pred.get_eta()
            display(pd.DataFrame(ret))

        return Response(json_data)