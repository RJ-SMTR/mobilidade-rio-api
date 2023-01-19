#from django.shortcuts import render
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response
from mobilidade_rio.predictor.models import *
from mobilidade_rio.predictor.serializers import *
import mobilidade_rio.pontos.models as gtfs_models
from django.db import connection
# import APIView
from rest_framework.views import APIView


class PredictorViewSet(viewsets.ModelViewSet):
    pass
