from django.conf.urls import url
from django.urls import include, path
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from mobilidade_rio.pontos import views

router = routers.DefaultRouter()
router.register(r'mode', views.ModeViewSet)
router.register(r'stop', views.StopViewSet, basename='stop')
router.register(r'qrcode', views.QrCodeViewSet, basename='qrcode')
router.register(r'linha', views.LinhaViewSet)
router.register(r'agency', views.AgencyViewSet)
router.register(r'route', views.RouteViewSet)
router.register(r'trip', views.TripViewSet, basename='trip')
router.register(r'sequence', views.SequenceViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^auth/', include('djoser.urls')),
    url(r'^auth/', include('djoser.urls.authtoken')),
]
