from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers, authtoken
from rest_framework.authtoken.views import obtain_auth_token

from mobilidade_rio.feedback import views as fb
from mobilidade_rio.pontos import views as gtfs
from mobilidade_rio.predictor import views as pred
from mobilidade_rio.routers import (
    GpsView,
    DadosView,
    DocumentedRouter,
    FeedbackApiView,
    GTFSView,
    MobilidadeRioApiView,
    router_with_uri_prefix,
)

from mobilidade_rio.dados import views as dados

gtfs_router = DocumentedRouter(GTFSView)
gtfs_router.register(r"agency", gtfs.AgencyViewSet)
gtfs_router.register(r"calendar", gtfs.CalendarViewSet)
gtfs_router.register(r"calendar_dates", gtfs.CalendarDatesViewSet)
gtfs_router.register(r"routes", gtfs.RoutesViewSet)
gtfs_router.register(r"trips", gtfs.TripsViewSet, basename="trips")
gtfs_router.register(r"shapes", gtfs.ShapesViewSet)
gtfs_router.register(r"stops", gtfs.StopsViewSet, basename="stops")
gtfs_router.register(r"stop_times", gtfs.StopTimesViewSet,
                     basename="stop_times")
gtfs_router.register(r"frequencies", gtfs.FrequenciesViewSet)
gtfs_router.register(
    r"upload", gtfs.UploadGtfsViewSet, basename="upload")

dados_gps_router = DocumentedRouter(GpsView)
dados_gps_router.register(r"sppo", dados.SppoViewSet, basename='sppo')

dados_router = DocumentedRouter(DadosView)
dados_router.registry.extend(
    router_with_uri_prefix(dados_gps_router, "gps/").registry)

pred_router = routers.DefaultRouter()
pred_router.register(r"predictor", pred.PredictorViewSet, basename='predictor')

feedback_router = DocumentedRouter(FeedbackApiView)
feedback_router.register(
    r"brt", fb.FeedbackBRTViewSet, basename="feedback_brt")

root_router = DocumentedRouter(MobilidadeRioApiView)
root_router.registry.extend(
    router_with_uri_prefix(gtfs_router, "gtfs/").registry)
root_router.registry.extend(router_with_uri_prefix(
    feedback_router, "feedback/").registry)
root_router.registry.extend(pred_router.registry)
root_router.registry.extend(
    router_with_uri_prefix(dados_router, "dados/").registry)
root_router.registry.extend(
    router_with_uri_prefix(dados_gps_router, "dados/gps/").registry)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(root_router.urls)),
    path("gtfs/", include(gtfs_router.urls)),
    path("feedback/", include(feedback_router.urls)),
    path("dados/", include(dados_router.urls)),
    path("dados/gps/", include(dados_gps_router.urls)),
    # Default routes
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("api-token-auth/", obtain_auth_token),
    url(r"^auth/", include("djoser.urls")),
    url(r"^auth/", include("djoser.urls.authtoken")),
]
