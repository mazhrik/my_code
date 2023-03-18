from rest_framework import serializers
from django.contrib.auth.models import (User, Group, Permission)
from account_management.models import Team_members, UserProfile, AccountSettings, Team, Team_members
from django.contrib.contenttypes.models import ContentType
import datetime
from rest_framework.serializers import SerializerMethodField


# from . models import UserData

class ContentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentType
        fields = ['app_label']


class PermissionSerializer(serializers.ModelSerializer):
    content_type = ContentTypeSerializer()

    class Meta:
        model = Permission
        fields = ('id', 'name', 'codename', 'content_type')


class UserAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username','first_name','last_name', 'email', 'is_active')


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'


class GroupSerializer(serializers.ModelSerializer):
    permissions = PermissionSerializer(many=True, read_only=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions')


class GroupSerializers(serializers.ModelSerializer):
    permissions = PermissionSerializer(read_only=True, many=True)

    class Meta:
        model = Group
        fields = ('id', 'name', 'permissions')


class UserAccountSerializerV1(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = "__all__"


class UserAccountTMO(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'groups', 'username')

class UserAccountSerializerVget(serializers.ModelSerializer):
    """
    only to list users data along groups name
    """
    groups = GroupSerializers(many=True, read_only=True)

    class Meta:
        model = User
        fields = ('id', 'is_active', 'first_name', 'last_name',
                  'username', 'email', 'is_staff', 'is_superuser', 'groups')


class AccountSettingSerializers(serializers.ModelSerializer):
    """
    Serializer to create account settings
    """

    class Meta:
        model = AccountSettings
        fields = '__all__'


class NewUserProfileSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = '__all__'


class NewUserSerializer(serializers.ModelSerializer):
    # groups = GroupSerializers(read_only=True)

    groups = SerializerMethodField('get_groups', allow_null=True, read_only=True)

    def get_groups(self, obj):
        try:
            return [u.name for u in obj.groups.all()]
        except:
            return None

    class Meta:
        model = User
        fields = ('id', 'is_active', 'first_name', 'last_name',
                  'username', 'email', 'is_staff', 'is_superuser', 'groups')


class TeamSerializer(serializers.ModelSerializer):
    team_leader_name = SerializerMethodField('get_team_leader_name', allow_null=True, read_only=True)

    def get_team_leader_name(self, obj):
        try:
            return obj.team_leader.username
        except:
            return None

    class Meta:
        model = Team
        fields = ('id','team_name', 'description','team_leader','team_leader_name')


class TeamMembersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team_members
        fields = ('id','team', 'user')


class TeamMembersSerializerForEdit(serializers.ModelSerializer):
    class Meta:
        
        model = Team_members
        fields = ('id','team', 'user')
        depth = 2

class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    user_id = serializers.IntegerField(required=True)
    new_password = serializers.CharField(required=True)