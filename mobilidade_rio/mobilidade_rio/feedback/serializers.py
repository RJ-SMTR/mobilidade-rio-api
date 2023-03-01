from mobilidade_rio.feedback.models import *
from rest_framework import serializers


class FeedbackBRTSerializer(serializers.ModelSerializer):
    # url = serializers.HyperlinkedRelatedField(view_name="stop_times-detail", read_only=True)
    # trip_id = TripsSerializer(read_only=True)
    # stop_id = StopsSerializer(read_only=True)

    class Meta:
        model = FeedbackBRT
        fields = [field.name for field in model._meta.fields]
        # fields.append("url")

    def save(self, **kwargs):
        return super().save(**kwargs)
