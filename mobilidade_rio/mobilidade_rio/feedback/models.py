from django.db import models
from django.core.exceptions import ValidationError
from django.http import HttpRequest
from django.template import  RequestContext

class FeedbackBRT(models.Model):
    """
    Feedback for GTFS BRT submitted by users.

    Fields
    ---
    - `like` (mandatory): true = thumbs up, false = thumbs down
    - `comment` (optional)
    - `stop_code` (mandatory): stop_code of current station
    - `stop_id` (optional): stop_id of selected platform
    - `route_id` (optional): route_id of selected bus
    """

    # get from client
    like = models.BooleanField(null=False)
    comment = models.TextField(null=True, blank=False, max_length=120)
    stop_code = models.TextField(null=False, blank=False, max_length=30)
    stop_id = models.TextField(null=True, blank=False, max_length=30)
    route_id = models.TextField(null=True, blank=False, max_length=30)

    # get automatically
    created_at = models.DateTimeField(auto_now_add=True)
    ip_address = models.TextField(null=True, blank=True)


    class Meta:
        """Rename table db name"""
        db_table = f"{__package__.rsplit('.', 1)[-1]}_brt"

    def __str__(self):
        like_dislike = "liked" if self.like else "disliked"
        comment = f" - {self.comment}" if self.comment else ""
        return f'{self.created_at}: {like_dislike}{comment}'
