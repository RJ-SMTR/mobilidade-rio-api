from django.conf.urls import url
from django.urls import include, path
from django.contrib import admin
from rest_framework import routers

from mobilidade_rio.pontos import views as gtfs
from mobilidade_rio.predictor import views as pred

gtfs_router = routers.DefaultRouter()
gtfs_router.register(r"agency", gtfs.AgencyViewSet)
gtfs_router.register(r"calendar", gtfs.CalendarViewSet)
gtfs_router.register(r"calendar_dates", gtfs.CalendarDatesViewSet)
gtfs_router.register(r"routes", gtfs.RoutesViewSet)
gtfs_router.register(r"trips", gtfs.TripsViewSet, basename="trips")
gtfs_router.register(r"shapes", gtfs.ShapesViewSet)
gtfs_router.register(r"stops", gtfs.StopsViewSet, basename="stops")
gtfs_router.register(r"stop_times", gtfs.StopTimesViewSet, basename="stop_times")
gtfs_router.register(r"frequencies", gtfs.FrequenciesViewSet)

pred_router = routers.DefaultRouter()
pred_router.register(r"shape_with_stops", pred.ShapeWithStopsViewSet,basename="shape_with_stops")
#pred_router.register(r"predictor", pred.PredictorViewSet,basename="pred_arrivals")


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("gtfs/", include(gtfs_router.urls)),
    path("predictor/", include(pred_router.urls)),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("predictor/shape_with_stops1/", pred.ShapeWithStopsView.as_view()),
    url(r"^auth/", include("djoser.urls")),
    url(r"^auth/", include("djoser.urls.authtoken")),
]
