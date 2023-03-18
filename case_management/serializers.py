from account_management.models import Team_members, Team
from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from rest_framework.fields import SerializerMethodField
from case_management.models import (Case, Location, Person,
                                    Investigator, Evidence,
                                    Media,
                                    CaseInvestigationMap, Shape, Event)
from keybase_management.models import Keybase
from keybase_management.serializers import KeybaseSerializer
from django.contrib.auth.models import User
from portfolio_management.serializers import AttachedPortfolioSerializer
from keybase_management.serializers import KeybaseSerializer


class LocationListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = '__all__'


class LocationsList(serializers.RelatedField):

    def to_representation(self, value):
        serializer = LocationListSerializer(value, read_only=True)
        return serializer.data


class CaseInvestigationMapSerializer(serializers.ModelSerializer):
    """
    Case Investigation Serializer
    """
    # location = LocationsList(many=True, queryset=Location.objects.all(), read_only=True)

    class Meta:
        model = CaseInvestigationMap
        fields = '__all__'


class ShapesSerializer(serializers.ModelSerializer):
    """
    Shape serializer
    """

    class Meta:
        model = Shape
        fields = '__all__'


class EventSerializer(serializers.ModelSerializer):
    """
    Event serializer
    """

    class Meta:
        model = Event
        fields = '__all__'


class MediaListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Media
        fields = '__all__'


class UserListSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'


class InvestigatorListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Investigator
        fields = '__all__'


class PersonListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Person
        fields = '__all__'


class EvidenceListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Evidence
        fields = '__all__'


class AttachInfo(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, Investigator):
            serializer = InvestigatorListSerializer(value)
        elif isinstance(value, Person):
            serializer = PersonListSerializer(value)
        elif isinstance(value, Location):
            serializer = LocationListSerializer(value)
        elif isinstance(value, Media):
            serializer = MediaListSerializer(value)
        elif isinstance(value, Evidence):
            serializer = EvidenceListSerializer(value)
        elif isinstance(value, CaseInvestigationMap):
            serializer = CaseInvestigationMapSerializer(value)
        elif isinstance(value, Event):
            serializer = EventSerializer(value)
        elif isinstance(value, Keybase):
            serializer = KeybaseSerializer(value)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data


class AttachedKeybaseSerializer(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, Keybase):
            serializer = KeybaseSerializer(value)

        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data


class CaseListSerializer(serializers.ModelSerializer):
    linked_data = AttachedPortfolioSerializer(many=True, queryset=ContentType.objects.all())
    investigators = AttachInfo(many=True, queryset=Investigator.objects.all())
    people = AttachInfo(many=True, queryset=Person.objects.all())
    locations = AttachInfo(many=True, queryset=Location.objects.all())
    media = AttachInfo(many=True, queryset=Media.objects.all())
    evidences = AttachInfo(many=True, queryset=Evidence.objects.all())
    case_map = AttachInfo(many=True, queryset=CaseInvestigationMap.objects.all())
    case_event = AttachInfo(many=True, queryset=Event.objects.all())
    # keybase = AttachedKeybaseSerializer(many=True, queryset=Keybase.objects.all())
    tao_investigator_name = SerializerMethodField('get_tao_investigator_name', allow_null=True, required=False, read_only=True)
    tmo_name = SerializerMethodField('get_tao_name', allow_null=True, required=False, read_only=True)

    def get_tao_name(self, obj):
        try:
            return Team_members.objects.filter(user=obj.tao_investigator).first().team.team_leader.username
        except:
            return None

    def get_tao_investigator_name(self, obj):
        try:
            return obj.tao_investigator.username
        except:
            return None

    class Meta:
        model = Case
        fields = '__all__'


class CaseListSerializerV2(serializers.ModelSerializer):
    created_on = SerializerMethodField('get_created', allow_null=True, required=False, read_only=True)
    updated_on = SerializerMethodField('get_updated_on', allow_null=True, required=False, read_only=True)
    expire_on = SerializerMethodField('get_expire_on', allow_null=True, required=False, read_only=True)
    incident_datetime = SerializerMethodField('get_incident_datetime', allow_null=True, required=False, read_only=True)

    def get_created(self, obj):
        try:
            return str(obj.created_on).replace("T", " ").split(".")[0]
        except:
            return obj.created_on

    def get_updated_on(self, obj):
        try:
            return str(obj.updated_on).replace("T", " ").split(".")[0]
        except:
            return obj.created_on
    def get_expire_on(self, obj):
        try:
            return str(obj.expire_on).replace("T", " ")
        except:
            return obj.created_on

    def get_incident_datetime(self, obj):
        try:
            return str(obj.incident_datetime).replace("T", " ")
        except:
            return obj.created_on
    

    class Meta:
        model = Case
        fields = '__all__'


class CaseDashboardsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = ('id', 'case_title', 'case_number', 'is_enabled', 'is_expired', 'created_on', 'case_type', 'case_priority',
                  'case_state', 'case_description','updated_on')