from rest_framework import serializers
from django.core.exceptions import ValidationError
from core_management.models import Notification, IPLogger, Log, AutoML, ImageAnalysisFRS, Log_history
from target_management.models import SocialTarget, KeybaseTarget, GenericTarget
from django.contrib.admin.models import LogEntry
from . import elasticsearch_handler_v2
from rest_framework.serializers import SerializerMethodField

es_object = elasticsearch_handler_v2.ElasticsearchHandler()


def validate_image(image):
    limit_size = 1000
    image_size = image.size / 1024
    print(image_size)
    if image_size > limit_size:
        raise ValidationError("Max size of file is {} KB".format(limit_size))


class NewsSerializer(serializers.Serializer):
    news_site = serializers.CharField(max_length=10)
    top = serializers.IntegerField(max_value=10)


class ImageSerializer(serializers.Serializer):
    image_url = serializers.URLField(max_length=100, allow_null=True)
    image = serializers.FileField(max_length=100, validators=[validate_image])


class NewsSearchSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=100)


class ToolsIdentifySerializer(serializers.Serializer):
    nationality = serializers.CharField(max_length=100)
    gender = serializers.CharField(max_length=10)
    age = serializers.IntegerField(max_value=80)


class ToolsDarkSerializer(serializers.Serializer):
    query = serializers.CharField(max_length=150)


class ToolsScrapperSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=10)
    query = serializers.CharField(max_length=150)


class ToolsTextSerializer(serializers.Serializer):
    type = serializers.CharField(max_length=100)
    query = serializers.CharField(max_length=5000)


class LookupIpSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=150)
    url = serializers.URLField(max_length=150)


class IpSerializer(serializers.Serializer):
    ip = serializers.CharField(max_length=50)


class DomainSerializer(serializers.Serializer):
    domain = serializers.CharField(max_length=50)


class TagResponseSerializer(serializers.Serializer):
    tag = serializers.CharField(max_length=50)


class NewsCrawelerSerializer(serializers.Serializer):
    channel = serializers.CharField(max_length=50)
    limit = serializers.IntegerField(max_value=10000)


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = '__all__'


class IPLoggerSerializer(serializers.ModelSerializer):
    class Meta:
        model = IPLogger
        fields = '__all__'


class SocialTargetsNotifications(serializers.ModelSerializer):
    class Meta:
        model = SocialTarget
        fields = ('user_names', 'target_status_string')


class KeybaseTargetNotification(serializers.ModelSerializer):
    class Meta:
        model = KeybaseTarget
        fields = ('keybase_title', 'target_status_string')


class GenericTargetNotification(serializers.ModelSerializer):
    class Meta:
        model = GenericTarget
        fields = ('title', 'target_status_string')


class LogSerializers(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = ("request_username", "request_method", "request_url","request_time",)


class LogHistorySerializers(serializers.ModelSerializer):
    class Meta:
        model = Log_history
        fields = '__all__'

class LogSerializersversion2(serializers.ModelSerializer):
    class Meta:
        model = Log
        fields = '__all__'


class TrainingKeywordsSerializer(serializers.Serializer):
    # tag = serializers.CharField(max_length=50)
    training_time = serializers.IntegerField()
    is_csv_file = serializers.BooleanField()
    csv_name = serializers.CharField()
    is_datawarehouse = serializers.BooleanField()
    training_from = serializers.IntegerField()
    training_to = serializers.IntegerField()
    file = serializers.FileField()
    # file_name = serializers.CharField()



class TrainingFileUploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    file_name = serializers.CharField()

class AutoMLSerializer(serializers.ModelSerializer):
    model_details = SerializerMethodField('get_model_details', allow_null=True, read_only=True)
    modified_status = SerializerMethodField('get_modified_status', allow_null=True, read_only=True)

    def get_model_details(self, obj):
        try:
            return es_object.get_ml_model(obj.model_name,obj.type)
        except:
            return None

    def get_modified_status(self, obj):
        try:
            if obj.status == "IN_PROGRESS":
                return "In Progress"
            elif obj.status == "DONE":
                return "Done"
            elif obj.status == "FAILED":
                return 'Failed'
            
        except:
            return None

    class Meta:
        model = AutoML
        fields = '__all__'

class ImageAnalysisFRSSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageAnalysisFRS
        fields = '__all__'