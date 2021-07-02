from rest_framework import viewsets
from rest_framework import permissions
from .models import Ponto, QrCode
from .serializers import PontoSerializer, QrCodeSerializer


class PontoViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Ponto.objects.all().order_by('identifier')
    serializer_class = PontoSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class QrCodeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = QrCode.objects.all().order_by('identifier')
    serializer_class = QrCodeSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
