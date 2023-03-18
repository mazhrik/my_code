from rest_framework import serializers
from .models import AvatarProfile, AddAccount, AvatarPostAction, AvatarReactionAction, AvatarCommentAction,\
                    AvatarMessageAction, AvatarShareAction
import json
from avatar_management.models import AvatarAddFriendAction
from rest_framework.serializers import SerializerMethodField

class AddAccountSerializer(serializers.ModelSerializer):
    group_list = SerializerMethodField('get_groups_list', allow_null=True, required=False, read_only=True)
    friends_list = SerializerMethodField('get_friends_list', allow_null=True, required=False, read_only=True)
    percentage = SerializerMethodField('get_success_rate_percentage', allow_null=True, required=False, read_only=True)
    
    def get_success_rate_percentage(self, obj):
        list_for_request=[]
        id=obj.id
        friend=AddAccount.objects.filter(id=id).first()
        friend_list_json = json.loads(friend.friends_list)
        counting_friend_request=AvatarAddFriendAction.objects.filter(account=id)
        for data in counting_friend_request:
            list_for_request.append(data.target_username)
        no_friend_request=len(set(list_for_request))       
        unique_list=set(list_for_request)
        count=0
        percentage=0
        if friend.social_media=='Facebook':
            if no_friend_request!=0:
                for each_name in unique_list:
                    for each_data in friend_list_json:
                        if each_name== each_data['username']:
                            count=count+1
                        else:
                            pass
                percentage=(count/no_friend_request)*100         
            else:
                pass
        else: 
            if no_friend_request!=0:
                for each_name in unique_list:
                    for each_data in friend_list_json:
                        if each_name== each_data['username_c']:
                            count=count+1
                        else:
                            pass
                percentage=(count/no_friend_request)*100         
            else:
                pass               
        return percentage    

    def get_friends_list(self, obj):
        return json.loads(obj.friends_list)
        
    def get_groups_list(self, obj):
        return json.loads(obj.friends_groups)    

    class Meta:
        model = AddAccount
        fields = ('id', 'username', 'password', 'email', 'social_media', 'friends_list', 'created_on', 'created_by', 'status','percentage','group_list')


class AvatarProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = AvatarProfile
        fields = '__all__'


class AvatarPostSerializer(serializers.ModelSerializer):

    account = AddAccountSerializer(read_only=True)

    class Meta:
        model = AvatarPostAction
        fields = ('id', 'post_text', 'post_date', 'account')


class AvatarCommentSerializer(serializers.ModelSerializer):
    account = AddAccountSerializer(read_only=True)

    class Meta:
        model = AvatarCommentAction
        fields = ['comment_text', 'target_post_url', 'comment_date', 'account']


class AvatarReactionSerializer(serializers.ModelSerializer):

    account = AddAccountSerializer(read_only=True)

    class Meta:
        model = AvatarReactionAction
        fields = ['reaction_type', 'target_post_url', 'reaction_date', 'account']


class AvatarMessageSerializer(serializers.ModelSerializer):

    account = AddAccountSerializer(read_only=True)

    class Meta:
        model = AvatarMessageAction
        fields = ['title', 'description', 'message_text', 'target_username', 'message_date', 'account']


class AvatarShareSerializer(serializers.ModelSerializer):
    account = AddAccountSerializer(read_only=True)

    class Meta:
        model = AvatarShareAction
        fields = ['post_text', 'target_post_url', 'share_date', 'account']


class SocialReloginSerializer(serializers.Serializer):
    id = serializers.CharField(max_length=255, default='')
    email = serializers.EmailField(max_length=255, default='')
    username = serializers.CharField(max_length=255, default='')
    social_media = serializers.CharField(max_length=255, default='')
    status = serializers.CharField(max_length=255, default='')
