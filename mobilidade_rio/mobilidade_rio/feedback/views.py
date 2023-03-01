from django.conf import settings
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from rest_framework import viewsets, permissions, mixins
from .models import FeedbackBRT
from .serializers import FeedbackBRTSerializer

@login_required
@require_POST
def submit_feedback_gtfs(request):
    """
    Submit feedback about if GTFS app info was useful.
    """
    feedback = FeedbackBRT(
        like=request.POST.get('like'),
        dislike=request.POST.get('dislike'),
        comment=request.POST.get('comment'),
        latitude=request.POST.get('latitude'),
        longitude=request.POST.get('longitude'),
    )
    feedback.save()

    return render(request, 'feedback/thank_you.html')

class FeedbackBRTViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    API endpoint that allows feedback to be viewed or submitted.
    """
    queryset = FeedbackBRT.objects.all()
    serializer_class = FeedbackBRTSerializer

    # TODO: if it's ok to use settings.DEBUG
    # if settings.SETTINGS_MODULE.rsplit('.',1)[-1] in ("native", "local"):
    permission_classes = [permissions.AllowAny]
    # else:
    #     permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        Save the feedback submission with the current user as the submitter.
        """

        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for
        else:
            ip = self.request.META.get('REMOTE_ADDR')

        if isinstance(ip, (list, tuple)):
            ip = ip[0]
        else:
            if ", " in ip:
                ip = ip.split(", ")[0]
            else:
                ip = ip.split(",")[0]

        serializer.save(ip_address=ip)

    def get_permissions(self):
        if self.request.method.upper() in ('OPTIONS'):
            return [permissions.IsAuthenticated()]
        return super().get_permissions()
