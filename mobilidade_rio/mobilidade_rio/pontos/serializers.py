from zipfile import is_zipfile
from mobilidade_rio.pontos.models import *
from rest_framework import serializers


class AgencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Agency
        fields = [field.name for field in model._meta.fields]


class CalendarSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Calendar
        fields = [field.name for field in model._meta.fields]


class CalendarDatesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = CalendarDates
        fields = [field.name for field in model._meta.fields]


class RoutesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Routes
        fields = [field.name for field in model._meta.fields]

        # show description of the route_type
        extra_kwargs = {
            # 'route_type': {'source': 'get_route_type_display'},
            # 'continuous_pickup': {'source': 'get_continuous_pickup_display'},
            # 'continuous_drop_off': {'source': 'get_continuous_drop_off_display'},
            # 'weelchair_accessible': {'source': 'get_weelchair_accessible_display'},
        }


class TripsSerializer(serializers.HyperlinkedModelSerializer):
    route_id = RoutesSerializer()

    class Meta:
        model = Trips
        fields = [field.name for field in model._meta.fields]


class ShapesSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Shapes
        fields = [field.name for field in model._meta.fields]


class StopsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Stops
        fields = [field.name for field in model._meta.fields]


class StopTimesSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedRelatedField(
        view_name="stop_times-detail", read_only=True)
    trip_id = TripsSerializer(read_only=True)
    stop_id = StopsSerializer(read_only=True)

    class Meta:
        model = StopTimes
        fields = [field.name for field in model._meta.fields]
        fields.append("url")


class FrequenciesSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedRelatedField(
        view_name="frequencies-detail", read_only=True)
    trip_id = TripsSerializer(read_only=True)

    class Meta:
        model = Frequencies
        fields = [field.name for field in model._meta.fields]
        fields.append("url")


class UploadGtfsSerializer(serializers.Serializer):
    """Serializer to upload GTFS"""
    gtfs_zip = serializers.FileField(
        help_text="Required. GTFS zip folder containing all GTFS files to upload."
    )

    ZIP_FILES_OPTIONS = (
        "agency",
        "calendar_dates",
        "calendar",
        "fare_attributes",
        "fare_rules",
        "feed_info",
        "frequencies",
        "routes",
        "shapes",
        "stop_times",
        "stops",
        "trips",
    )
    zip_files = serializers.CharField(
        required=False, allow_blank=False, allow_null=False,
        help_text=f"Optional. Filter which gtfs files inside zip to upload. &nbsp\
            Example: 'stops,stop_times' Options: {', '.join(ZIP_FILES_OPTIONS)}"
    )

    def validate_zip_files(self, value: str):
        """Validate and transform to list"""
        files = value.split(",")
        for file in files:
            if file not in self.ZIP_FILES_OPTIONS:
                raise serializers.ValidationError(
                    f"file '{file}' should be one of these options: {self.ZIP_FILES_OPTIONS}")
        return value
