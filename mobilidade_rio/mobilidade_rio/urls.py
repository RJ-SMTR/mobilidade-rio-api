from django.conf.urls import url
from django.urls import include, path
from django.contrib import admin
from django.urls import path
from rest_framework import routers

from mobilidade_rio.pontos import views

router = routers.DefaultRouter()
router.register(r'pontos', views.PontoViewSet)
router.register(r'qrcodes', views.QrCodeViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^auth/', include('djoser.urls')),
    url(r'^auth/', include('djoser.urls.authtoken')),
]
