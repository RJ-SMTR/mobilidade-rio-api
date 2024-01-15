"""
Utils for routers
"""


from rest_framework import routers

# utils


def router_with_uri_prefix(
    router: routers.DefaultRouter,
    prefix_uri: str
) -> routers.DefaultRouter:
    """
    Adds a prefix URI to each URL pattern in the given router.
    """

    new_router = routers.DefaultRouter()

    for route in router.registry:
        prefix, viewset, basename = route
        prefix = f"{prefix_uri}{prefix}"
        new_router.register(prefix, viewset, basename)

    return new_router


# router views

class MobilidadeRioApiView(routers.APIRootView):
    """
    All endpoints for this API.
    """


class GTFSView(routers.APIRootView):
    """
    Endpoints for GTFS tables.
    """


class FeedbackApiView(routers.APIRootView):
    """
    Endpoints for feedback APIs.
    """


# router

class DocumentedRouter(routers.DefaultRouter):
    """
    This router allows to use custom APIRoot pages, with custom title and description.
    """

    def __init__(self, api_root_view: routers.APIRootView, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.APIRootView = api_root_view  # pylint: disable=C0103
