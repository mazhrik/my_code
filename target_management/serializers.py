
from django.contrib.auth.models import User
from rest_framework import serializers
from target_management.models import  LeakedData, SocialTarget, GenericTarget, KeybaseTarget
from target_management.models import SocialTarget, GenericTarget, KeybaseTarget, UserNews
from report_management.models import ReportsNotes
from keybase_management.models import Keybase
from target_management.constants import TARGET_INDEX_RESOLVE, INDEX_LIST, KEYBASE_INDEX_LIST, GENERIC_INDEX_LIST, \
    INDEX_PLATFORM_ALL
from rest_framework.serializers import SerializerMethodField
from target_management.constants import TARGET_SUB_TYPE, TARGET_TYPE, TARGET_INDEX_RESOLVE, KEYBASE_INDEX_LIST
# from target_management.views import get_target_object
from core_management import elasticsearch_handler_v2
from django.contrib.contenttypes.models import ContentType




es_object = elasticsearch_handler_v2.ElasticsearchHandler()
def get_index_for_es(target_type, target_sub_type, index):
    to_translate = str(target_type) + ',' + str(target_sub_type)
    translate_target = dict(TARGET_INDEX_RESOLVE)
    index_translated = translate_target[str(to_translate)]
    return_index = index_translated + index
    return return_index

def get_attribute(target_type, sub_target_type):
    translate_target = dict(TARGET_TYPE)
    translate_subtarget = dict(TARGET_SUB_TYPE)
    target_type_translated = translate_target[str(target_type)]
    target_sub_type_translated = translate_subtarget[str(sub_target_type)]
    return target_type_translated, target_sub_type_translated

def get_index_for_es(target_type, target_sub_type, index):
    to_translate = str(target_type) + ',' + str(target_sub_type)
    translate_target = dict(TARGET_INDEX_RESOLVE)
    index_translated = translate_target[str(to_translate)]
    return_index = index_translated + index
    return return_index

def get_target_object(target_type=None, target_id=None, gtr=None):
    if gtr:
        type_gtr = gtr.split('_')[0]
        if type_gtr == 'st':
            specific_object = SocialTarget.objects.get(GTR=gtr)
            target_type = 'social'
        elif type_gtr == 'dt':
            specific_object = GenericTarget.objects.get(GTR=gtr)
            target_type = 'generic'
        elif type_gtr == 'kb':
            specific_object = KeybaseTarget.objects.get(GTR=gtr)
            target_type = 'keybase'
        else:
            specific_object = None

    elif target_type == 'social':
        if SocialTarget.objects.filter(id=target_id):
            specific_object = SocialTarget.objects.filter(id=target_id).first()
        else:
            specific_object = None

    elif target_type == 'keybase':
        if KeybaseTarget.objects.filter(id=target_id):
            specific_object = KeybaseTarget.objects.filter(id=target_id).first()
        else:
            specific_object = None

    elif target_type == 'generic':
        if GenericTarget.objects.filter(id=target_id):
            specific_object = GenericTarget.objects.filter(id=target_id).first()
        else:
            specific_object = None
    else:
        specific_object = None
    return specific_object, target_type


class SocialTargetListSerializerV1(serializers.ModelSerializer):
    user = SerializerMethodField('get_user', allow_null=True, read_only=True)

    def get_user(self, obj):
        try:
            return obj.user.username
        except:
            return None

    class Meta:
        model = SocialTarget
        fields = '__all__'


class SocialTargetListSerializer(serializers.ModelSerializer):
    # file_size = SerializerMethodField('get_file_size', allow_null=True, read_only=True)
    # string_target_summary = SerializerMethodField('get_target_summary', allow_null=True, read_only=True)
    # username = SerializerMethodField('get_username', allow_null=True, read_only=True)
    # descriptions = SerializerMethodField('get_descriptions', allow_null=True, read_only=True)
    # location_details = SerializerMethodField('get_location_details', allow_null=True, read_only=True)
    
    # def get_username(self,obj):
    #     try:
    #         return User.objects.filter(username=obj.user).first().username
    #     except:
    #         return None
           
    

    # def get_file_size(self, obj):
    #     try:
    #         gtr = obj.GTR
    #         # specific_object, target_type = get_target_object(gtr=gtr)
    #         target_type_es, target_sub_type_es = get_attribute(target_type=obj.target_type,
    #                                                                     sub_target_type=obj.target_sub_type)
    #         size = es_object.get_filesize(gtr,target_type_es,target_sub_type_es)    
            
    #         if size == False:
    #             return None 
    #         return size
    #     except Exception as e:
    #         return None

    # def get_target_summary(self,obje):
    #     try:
    #         gtr_value = obje.GTR
    #         target_type = obje.target_type
    #         target_sub_type = obje.target_sub_type
    
    #         target_type_es, target_sub_type_es = get_attribute(target_type=target_type,
    #                                                                     sub_target_type=target_sub_type)
    #         index_es = get_index_for_es(target_type_es, target_sub_type_es, "data_mining")
    #         res_list, count = es_object.get_response_by_gtr(index_es, gtr_value, 100)
    #         return res_list
    #     except:
    #         return None    
    
        
    # def get_descriptions(self, obj):
    #     #profile_information
    #     try:
    #         gtr = obj.GTR
    #         specific_object, target_type = get_target_object(gtr=gtr)
    #         target_type_es, target_sub_type_es = get_attribute(target_type=obj.target_type,
    #                                                             sub_target_type=obj.target_sub_type)
    #         index_es = get_index_for_es(target_type_es, target_sub_type_es, "profile_information")
    #         res_list, count = es_object.get_response_by_gtr(index_es, gtr)
    #         return res_list
    #     except Exception as e:
    #         return []

    # # location_details

    # def get_location_details(self, obj):
    #     #profile_information
    #     try:
    #         gtr = obj.GTR
    #         # specific_object, target_type = get_target_object(gtr=gtr)
    #         target_type_es, target_sub_type_es = get_attribute(target_type=obj.target_type,
    #                                                             sub_target_type=obj.target_sub_type)
    #         index_es = get_index_for_es(target_type_es, target_sub_type_es, "location_details")
    #         res_list, count = es_object.get_response_by_gtr(index_es, gtr)
    #         return res_list
    #     except Exception as e:
    #         return []
    class Meta:
        model = SocialTarget
        fields = '__all__'


class SocialTargetListSerializerV2(serializers.ModelSerializer):
    file_size = SerializerMethodField('get_file_size', allow_null=True, read_only=True)
    string_target_summary = SerializerMethodField('get_target_summary', allow_null=True, read_only=True)
    username = SerializerMethodField('get_username', allow_null=True, read_only=True)
    descriptions = SerializerMethodField('get_descriptions', allow_null=True, read_only=True)
    location_details = SerializerMethodField('get_location_details', allow_null=True, read_only=True)
    target_type_ = SerializerMethodField('get_target_type_', allow_null=True, read_only=True)
    
    

    def get_target_type_(self, obj):

        if obj.GTR:
            type_gtr = obj.GTR.split('_')[0]
            if type_gtr == 'st':
                target_type = 'social'
            elif type_gtr == 'dt':
                target_type = 'generic'
            elif type_gtr == 'kb':
                target_type = 'keybase'
            else:
                target_type = None
 
        return target_type

    def get_username(self,obj):
        try:
            return User.objects.filter(username=obj.user).first().username
        except:
            return None
           
    

    def get_file_size(self, obj):
        try:
            gtr = obj.GTR
            # specific_object, target_type = get_target_object(gtr=gtr)
            target_type_es, target_sub_type_es = get_attribute(target_type=obj.target_type,
                                                                        sub_target_type=obj.target_sub_type)
            size = es_object.get_filesize(gtr,target_type_es,target_sub_type_es)    
            
            if size == False:
                return None 
            return size
        except Exception as e:
            return None

    def get_target_summary(self,obje):
        try:
            gtr_value = obje.GTR
            target_type = obje.target_type
            target_sub_type = obje.target_sub_type
    
            target_type_es, target_sub_type_es = get_attribute(target_type=target_type,
                                                                        sub_target_type=target_sub_type)
            index_es = get_index_for_es(target_type_es, target_sub_type_es, "data_mining")
            res_list, count = es_object.get_response_by_gtr(index_es, gtr_value, 100)
            return res_list
        except:
            return None    
    
        
    def get_descriptions(self, obj):
        #profile_information
        try:
            gtr = obj.GTR
            specific_object, target_type = get_target_object(gtr=gtr)
            target_type_es, target_sub_type_es = get_attribute(target_type=obj.target_type,
                                                                sub_target_type=obj.target_sub_type)
            index_es = get_index_for_es(target_type_es, target_sub_type_es, "profile_information")
            res_list, count = es_object.get_response_by_gtr(index_es, gtr)
            return res_list
        except Exception as e:
            return []

    # location_details

    def get_location_details(self, obj):
        #profile_information
        try:
            gtr = obj.GTR
            # specific_object, target_type = get_target_object(gtr=gtr)
            target_type_es, target_sub_type_es = get_attribute(target_type=obj.target_type,
                                                                sub_target_type=obj.target_sub_type)
            index_es = get_index_for_es(target_type_es, target_sub_type_es, "location_details")
            res_list, count = es_object.get_response_by_gtr(index_es, gtr)
            return res_list
        except Exception as e:
            return []
    class Meta:
        model = SocialTarget
        fields = '__all__'


class GenericTargetListSerializer(serializers.ModelSerializer):

    # file_size = SerializerMethodField('get_file_size', allow_null=True, read_only=True)
    username = SerializerMethodField('get_username', allow_null=True, read_only=True)
    
    def get_username(self,obj):
        try:
            return User.objects.filter(username=obj.user).first().username
        except:
            return None

    # def get_file_size(self, obj):
    #     try:
    #         gtr = obj.GTR
    #         specific_object, target_type = get_target_object(gtr=gtr)
    #         target_type_es, target_sub_type_es = get_attribute(target_type=specific_object.target_type,
    #                                                                     sub_target_type=specific_object.target_sub_type)
    #         size = es_object.get_filesize(gtr,target_type_es,target_sub_type_es) 
    #         if size == False:
    #             return None 
    #         return size
    #     except Exception as e:
    #         return None
        
    class Meta:
        model = GenericTarget
        fields = '__all__'


class GenericTargetListSerializerV2(serializers.ModelSerializer):

    file_size = SerializerMethodField('get_file_size', allow_null=True, read_only=True)
    username = SerializerMethodField('get_username', allow_null=True, read_only=True)
    user_names = SerializerMethodField('get_user_names', allow_null=True, read_only=True)

    target_type_ = SerializerMethodField('get_target_type_', allow_null=True, read_only=True)
    
    

    def get_target_type_(self, obj):

        if obj.GTR:
            type_gtr = obj.GTR.split('_')[0]
            if type_gtr == 'st':
                target_type = 'social'
            elif type_gtr == 'dt':
                target_type = 'generic'
            elif type_gtr == 'kb':
                target_type = 'keybase'
            else:
                target_type = None
 
        return target_type

    def get_user_names(self, obj):
        try:
            return obj.title
        except:
            return None
    
    def get_username(self,obj):
        try:
            return User.objects.filter(username=obj.user).first().username
        except:
            return None

    def get_file_size(self, obj):
        try:
            gtr = obj.GTR
            specific_object, target_type = get_target_object(gtr=gtr)
            target_type_es, target_sub_type_es = get_attribute(target_type=specific_object.target_type,
                                                                        sub_target_type=specific_object.target_sub_type)
            size = es_object.get_filesize(gtr,target_type_es,target_sub_type_es) 
            if size == False:
                return None 
            return size
        except Exception as e:
            return None
        
    class Meta:
        model = GenericTarget
        fields = '__all__'


class GenericTargetListSerializerV1(serializers.ModelSerializer):

    user = SerializerMethodField('get_user', allow_null=True, read_only=True)

    def get_user(self, obj):
        try:
            return obj.user.username
        except:
            return None
        
    class Meta:
        model = GenericTarget
        fields = '__all__'


class KeybaseTargetListSerializer(serializers.ModelSerializer):
    username = SerializerMethodField('get_username', allow_null=True, read_only=True)
    def get_username(self,obj):
        try:
            return User.objects.filter(username=obj.user).first().username
        except:
            return None

    # keybase=SerializerMethodField()
    # available = SerializerMethodField('get_available', allow_null=True, read_only=True)
    phrases = SerializerMethodField('get_phrases', allow_null=True, read_only=True)
    hashtags = SerializerMethodField('get_hashtags', allow_null=True, read_only=True)
    mentions = SerializerMethodField('get_mentions', allow_null=True, read_only=True)
    # file_size = SerializerMethodField('get_file_size', allow_null=True, read_only=True)


    def get_phrases(self, obj):
        try:
            return obj.keybase.phrases
        except:
            return None

    def get_hashtags(self, obj):
        try:
            return obj.keybase.hashtags
        except:
            return None
    def get_mentions(self, obj):
        try:
            return obj.keybase.mentions
        except:
            return None        

    

    # def get_file_size(self, obj):
    #     try:
    #         gtr = obj.GTR
    #         specific_object, target_type = get_target_object(gtr=gtr)
    #         target_type_es, target_sub_type_es = get_attribute(target_type=specific_object.target_type,
    #                                                                     sub_target_type=specific_object.target_sub_type)
    #         size = es_object.get_filesize(gtr,target_type_es,target_sub_type_es)    
            
    #         if size == False:
    #             return None 
    #         return size
    #     except Exception as e:
    #         return None
        

    # def get_available(self, obj):
    #     try:
    #         gtr=obj.GTR
    #         keybase_status=[]
    #         available_key=False
    #         keybase_target_marked=KeybaseTarget.objects.filter(GTR=gtr).first()
    #         keybase_status=keybase_target_marked.target_status_string
    #         keybase_status_split=keybase_status.split(',')
    #         if keybase_status_split[-1]=='Successful! data store to BDS ':
    #             available_key = True
    #             return available_key
    #         else:
    #             available_key = False
    #             return available_key
    #     except:
    #         return False
    class Meta:
        model = KeybaseTarget
        fields = '__all__'


class GTRArchiveTargetSerializer(serializers.RelatedField):

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


class KeybaseTargetListSerializerV2(serializers.ModelSerializer):
    username = SerializerMethodField('get_username', allow_null=True, read_only=True)
    target_type_ = SerializerMethodField('get_target_type_', allow_null=True, read_only=True)
    
    

    def get_target_type_(self, obj):

        if obj.GTR:
            type_gtr = obj.GTR.split('_')[0]
            if type_gtr == 'st':
                target_type = 'social'
            elif type_gtr == 'dt':
                target_type = 'generic'
            elif type_gtr == 'kb':
                target_type = 'keybase'
            else:
                target_type = None
 
        return target_type


    def get_username(self,obj):
        try:
            return User.objects.filter(username=obj.user).first().username
        except:
            return None

    elastic_count=SerializerMethodField("get_elastic_count", allow_null=True, read_only=True)

    def get_elastic_count(self, obj):

        index_list = KEYBASE_INDEX_LIST
        data = {}
        for index in index_list:
            try:
                target_type_es, target_sub_type_es = get_attribute(obj.target_type , obj.target_sub_type)
                index_es = get_index_for_es(target_type_es, target_sub_type_es, str(index))
                res_list, count = es_object.get_response_by_gtr(index_es, obj.GTR, 200)
                if index == "news_data":
                    news = {}
                    for each_news in res_list:
                        if each_news['source']["title"] not in news:
                            news[each_news['source']["title"]]= 0
                        else:
                            news[each_news['source']["title"]] = news[each_news['source']["title"]] + 1


                    data[index]=  [ {"news":key, "count":value}  for key, value in  news.items()]  
                else:
                    data[index]= len(res_list)
            except:
                pass
        return data
            
        

    available = SerializerMethodField('get_available', allow_null=True, read_only=True)
    phrases = SerializerMethodField('get_phrases', allow_null=True, read_only=True)
    hashtags = SerializerMethodField('get_hashtags', allow_null=True, read_only=True)
    mentions = SerializerMethodField('get_mentions', allow_null=True, read_only=True)
    file_size = SerializerMethodField('get_file_size', allow_null=True, read_only=True)
    user_names = SerializerMethodField('get_user_names', allow_null=True, read_only=True)

    def get_user_names(self, obj):
        try:
            return obj.keybase_title
        except:
            return None


    def get_phrases(self, obj):
        try:
            return obj.keybase.phrases
        except:
            return None

    def get_hashtags(self, obj):
        try:
            return obj.keybase.hashtags
        except:
            return None
    def get_mentions(self, obj):
        try:
            return obj.keybase.mentions
        except:
            return None        

    

    def get_file_size(self, obj):
        try:
            gtr = obj.GTR
            specific_object, target_type = get_target_object(gtr=gtr)
            target_type_es, target_sub_type_es = get_attribute(target_type=specific_object.target_type,
                                                                        sub_target_type=specific_object.target_sub_type)
            size = es_object.get_filesize(gtr,target_type_es,target_sub_type_es)    
            
            if size == False:
                return None 
            return size
        except Exception as e:
            return None
        

    def get_available(self, obj):
        try:
            gtr=obj.GTR
            keybase_status=[]
            available_key=False
            keybase_target_marked=KeybaseTarget.objects.filter(GTR=gtr).first()
            keybase_status=keybase_target_marked.target_status_string
            keybase_status_split=keybase_status.split(',')
            if keybase_status_split[-1]=='Successful! data store to BDS ':
                available_key = True
                return available_key
            else:
                available_key = False
                return available_key
        except:
            return False
    class Meta:
        model = KeybaseTarget
        fields = '__all__'


class TargetResponseSerializer(serializers.Serializer):
    target_type = serializers.CharField(max_length=10, allow_null=True)
    GTR = serializers.CharField(max_length=70, allow_null=True)
    target_id = serializers.IntegerField(max_value=1000, allow_null=True)


class TargetLinkAnalysisResponseSerializer(serializers.Serializer):
    gtr = serializers.CharField(max_length=100)


class SocialMediaAccountSettings(serializers.Serializer):
    social_media = serializers.CharField()
    username = serializers.CharField()
    status = serializers.CharField()
    email = serializers.CharField()
    password = serializers.CharField()

    class Meta:
        fields = '__all__'


class ReportsNotesSerialized(serializers.ModelSerializer):
    class Meta:
        model = ReportsNotes
        fields = '__all__'
class Leaked_data_serializer(serializers.ModelSerializer):

    user = SerializerMethodField('get_user', allow_null=True, read_only=True)

    def get_user(self, obj):
        try:
            return obj.user.username
        except:
            return None
    class Meta:
        model = LeakedData
        fields = '__all__'

class UserNewsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserNews
        fields = "__all__"


class TargetShareResourceSerializer(serializers.Serializer):
    target_id = serializers.IntegerField(required=True)
    target_type = serializers.CharField(required=True, max_length=100)
    user = serializers.IntegerField(required=True)