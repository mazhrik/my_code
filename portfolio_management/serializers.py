from functools import wraps

from django.db.models.query import QuerySet

from .models import Individual, Group, Event, LinkedData, Portfolio
from .models import Event as PortfolioEvent
from django.contrib.auth.models import User
from target_management.serializers import *
from keybase_management.serializers import *
from django.contrib.contenttypes.models import ContentType
from case_management.models import *
from django_currentuser import *
# from case_management.serializers import CaseListSerializer
from rest_framework.serializers import SerializerMethodField
from target_management.constants import  KEYBASE_INDEX_LIST



def aslist(func):
    def iflist(a):
        if type(a) is not str:
            return str(a)
        else:
            return a

    @wraps(func)
    def wrapper(*args, **kwds):
        args = map(iflist, args)
        return func(*args, **kwds)

    return wrapper


class CaseListSerializerBasic(serializers.ModelSerializer):
    class Meta:
        model = Case
        exclude = ['linked_data', 'investigators', 'people', 'locations', 'media', 'evidences', 'case_event',
                   'case_map']


class LinkedDataSerializer(serializers.ModelSerializer):
    type_update = SerializerMethodField('get_type_update', allow_null=True, read_only=True)


    def get_type_update(self, obj):
        try:
            return obj.type
        except:
            return None 
    class Meta:
        model = LinkedData
        fields = '__all__'



class IndividualSerializer(serializers.ModelSerializer):
    class Meta:
        model = Individual
        # exclude = ['target', 'keybase', 'portfolio', 'linked_data']
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # exclude = ['target', 'keybase', 'portfolio', 'linked_data']
        fields = '__all__'
class portfolioserializer(serializers.ModelSerializer):
    class Meta:
        model = Portfolio
        fields = '__all__'

# class portfolioserializercase(serializers.ModelSerializer):
#     case=CaseListSerializer(many=True,QuerySet=Case.objects.all())

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        exclude = ['target', 'keybase', 'portfolio', 'linked_data']


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioEvent
        exclude = ['target', 'keybase', 'portfolio', 'linked_data']





class AttachedTargetSerializer(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, SocialTarget):
            serializer = SocialTargetListSerializerV2(value)
        elif isinstance(value, KeybaseTarget):
            serializer = KeybaseTargetListSerializerV2(value)
        elif isinstance(value, GenericTarget):
            serializer = GenericTargetListSerializerV2(value)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data

class AttachedTargetSerializerV1(serializers.RelatedField):

    def to_representation(self, value):
        if isinstance(value, SocialTarget):
            serializer = SocialTargetListSerializerV1(value)
        elif isinstance(value, KeybaseTarget):
            serializer = KeybaseTargetListSerializer(value)
        elif isinstance(value, GenericTarget):
            serializer = GenericTargetListSerializerV1(value)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data




class AttachedPortfolioSerializer(serializers.RelatedField):
    def to_representation(self, value):
        if isinstance(value, PortfolioEvent):
            serializer = EventSerializer(value)
        elif isinstance(value, Individual):
            serializer = IndividualSerializer(value)
        elif isinstance(value, Group):
            serializer = GroupSerializer(value)
        elif isinstance(value, SocialTarget):
            serializer = SocialTargetListSerializer(value)
        elif isinstance(value, KeybaseTarget):
            serializer = KeybaseTargetListSerializer(value)
        elif isinstance(value, GenericTarget):
            serializer = GenericTargetListSerializer(value)
        elif isinstance(value, LinkedData):
            serializer = LinkedDataSerializer(value)
        elif isinstance(value, Keybase):
            serializer = KeybaseSerializer(value)
        else:
            raise Exception('Unexpected type of tagged object')

        return serializer.data


class AttachedKeybaseSerializer(serializers.RelatedField):

    def to_representation(self, value):
        serializer = KeybaseSerializer(value)
        return serializer.data


class AttachCaseSerializer(serializers.RelatedField):

    def to_representation(self, value):
        serializer = CaseListSerializerBasic(value)
        return serializer.data


class AttachLinkedDataSerializer(serializers.RelatedField):

    def to_representation(self, value):
        serializer = LinkedDataSerializer(value)
        return serializer.data


class EventSerializerV1(serializers.ModelSerializer):
    target = AttachedTargetSerializer(many=True, queryset=ContentType.objects.all())
    keybase = AttachedKeybaseSerializer(many=True, queryset=Keybase.objects.all())
    portfolio = AttachedPortfolioSerializer(many=True, queryset=ContentType.objects.all())
    linked_data = AttachLinkedDataSerializer(many=True, queryset=LinkedData.objects.all())
    case = AttachCaseSerializer(many=True, queryset=Case.objects.all())

    class Meta:
        model = PortfolioEvent
        fields = '__all__'

class EventSerializerV2(serializers.ModelSerializer):
    target = AttachedTargetSerializerV1(many=True, queryset=ContentType.objects.all())
    keybase = AttachedKeybaseSerializer(many=True, queryset=Keybase.objects.all())
    portfolio = AttachedPortfolioSerializer(many=True, queryset=ContentType.objects.all())
    linked_data = AttachLinkedDataSerializer(many=True, queryset=LinkedData.objects.all())
    case = AttachCaseSerializer(many=True, queryset=Case.objects.all())

    class Meta:
        model = PortfolioEvent
        fields = '__all__'

list_str = ""
flag_phone = True


class TrackListingField(serializers.RelatedField):

    def to_representation(self, value):
        global list_str
        global flag_phone
        print(value)
        duration = value
        print("here", value)
        if duration in {'{', '}'}:
            pass
        else:
            list_str = list_str + str(duration)
            flag_phone = False
            return list_str


class IndividualSerializerV1(serializers.ModelSerializer):
    target = AttachedTargetSerializer(many=True, queryset=ContentType.objects.all())
    keybase = AttachedKeybaseSerializer(many=True, queryset=Keybase.objects.all())
    portfolio = AttachedPortfolioSerializer(many=True, queryset=ContentType.objects.all())
    linked_data = AttachLinkedDataSerializer(many=True, queryset=LinkedData.objects.all())
    case = AttachCaseSerializer(many=True, queryset=Case.objects.all())

    class Meta:
        model = Individual
        fields = '__all__'


class GroupSerializerV1(serializers.ModelSerializer):
    target = AttachedTargetSerializer(many=True, queryset=ContentType.objects.all())
    keybase = AttachedKeybaseSerializer(many=True, queryset=Keybase.objects.all())
    portfolio = AttachedPortfolioSerializer(many=True, queryset=ContentType.objects.all())
    linked_data = AttachLinkedDataSerializer(many=True, queryset=LinkedData.objects.all())
    case = AttachCaseSerializer(many=True, queryset=Case.objects.all())

    class Meta:
        model = Group
        fields = '__all__'

class GroupSerializerV2(serializers.ModelSerializer):
    target = AttachedTargetSerializerV1(many=True, queryset=ContentType.objects.all())
    keybase = AttachedKeybaseSerializer(many=True, queryset=Keybase.objects.all())
    portfolio = AttachedPortfolioSerializer(many=True, queryset=ContentType.objects.all())
    linked_data = AttachLinkedDataSerializer(many=True, queryset=LinkedData.objects.all())
    case = AttachCaseSerializer(many=True, queryset=Case.objects.all())

    class Meta:
        model = Group
        fields = '__all__'



class NewIndividualSerializer(serializers.ModelSerializer):
    target = AttachedTargetSerializer(many=True, queryset=ContentType.objects.all())
    keybase = AttachedKeybaseSerializer(many=True, queryset=Keybase.objects.all())
    portfolio = AttachedPortfolioSerializer(many=True, queryset=ContentType.objects.all())
    linked_data = AttachLinkedDataSerializer(many=True, queryset=LinkedData.objects.all())
    case = AttachCaseSerializer(many=True, queryset=Case.objects.all())

    class Meta:
        model = Individual
        fields = '__all__'

class NewIndividualSerializerV1(serializers.ModelSerializer):
    target = AttachedTargetSerializerV1(many=True, queryset=ContentType.objects.all())
    keybase = AttachedKeybaseSerializer(many=True, queryset=Keybase.objects.all())
    portfolio = AttachedPortfolioSerializer(many=True, queryset=ContentType.objects.all())
    linked_data = AttachLinkedDataSerializer(many=True, queryset=LinkedData.objects.all())
    case = AttachCaseSerializer(many=True, queryset=Case.objects.all())

    class Meta:
        model = Individual
        fields = '__all__'
