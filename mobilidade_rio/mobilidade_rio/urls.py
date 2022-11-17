from django.conf.urls import url
from django.urls import include, path
from django.contrib import admin
from rest_framework import routers

from mobilidade_rio.pontos import views

router = routers.DefaultRouter()
router.register(r"agency", views.AgencyViewSet)
router.register(r"calendar", views.CalendarViewSet)
router.register(r"calendar_dates", views.CalendarDatesViewSet)
router.register(r"routes", views.RoutesViewSet)
router.register(r"trips", views.TripsViewSet, basename="trips")
router.register(r"shapes", views.ShapesViewSet)
router.register(r"stops", views.StopsViewSet, basename="stops")
router.register(r"stop_times", views.StopTimesViewSet, basename="stop_times")
router.register(r"frequencies", views.FrequenciesViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("gtfs/", include(router.urls)),
    path("admin/", admin.site.urls),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    url(r"^auth/", include("djoser.urls")),
    url(r"^auth/", include("djoser.urls.authtoken")),
]
