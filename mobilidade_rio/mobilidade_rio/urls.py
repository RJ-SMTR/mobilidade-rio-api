from django.conf.urls import url
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers

from mobilidade_rio.feedback import views as fb
from mobilidade_rio.pontos import views as gtfs
from mobilidade_rio.predictor import views as pred
from mobilidade_rio.routers import (
    DocumentedRouter,
    FeedbackApiView,
    GTFSView,
    MobilidadeRioApiView,
    router_with_uri_prefix,
)

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

pred_router = routers.DefaultRouter()
pred_router.register(r"predictor", pred.PredictorViewSet, basename='predictor')

feedback_router = DocumentedRouter(FeedbackApiView)
feedback_router.register(r"brt", fb.FeedbackBRTViewSet,
                         basename="feedback_brt")

root_router = DocumentedRouter(MobilidadeRioApiView)
root_router.registry.extend(
    router_with_uri_prefix(gtfs_router, "gtfs/").registry)
root_router.registry.extend(router_with_uri_prefix(
    feedback_router, "feedback/").registry)
root_router.registry.extend(pred_router.registry)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("", include(root_router.urls)),
    path("gtfs/", include(gtfs_router.urls)),
    path("feedback/", include(feedback_router.urls)),

    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    url(r"^auth/", include("djoser.urls")),
    url(r"^auth/", include("djoser.urls.authtoken")),
]
