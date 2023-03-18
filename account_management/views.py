from django.contrib.auth import authenticate
from django.contrib.auth.models import (User, Group, Permission)
from django_eventstream import send_event
from rest_framework import status, permissions, pagination
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import TokenAuthentication
from django.http import JsonResponse
import datetime
from .models import UserActivity, Team, Team_members
from .password_validation import validate_password
from core_management.views import send_notification
from .serializers import (UserAccountSerializer,
                          UserProfileSerializer,
                          UserAccountSerializerV1,
                          GroupSerializer, PermissionSerializer, UserAccountSerializerVget, GroupSerializers,
                          AccountSettingSerializers, NewUserSerializer, TeamSerializer, TeamMembersSerializer, UserAccountTMO, ChangePasswordSerializer, TeamMembersSerializerForEdit)
from .models import UserProfile, AccountSettings
from portfolio_management.views import perform_date_change
from rest_framework.response import Response
from core_management.license_controller import limit_check
import json
from rest_framework.decorators import action
from django.db.models import Q
from django.db import transaction
from django.utils import timezone
import time


from rest_framework.renderers import JSONRenderer

class IsSuperUser(IsAdminUser):
    """

    permission to superuser only

    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_superuser)


class AddUserViewSet(ModelViewSet):
    """
     All users operations will performed
    """

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1' and self.action == 'list':
            return UserAccountSerializerVget
        elif self.action == 'retrieve':
            return UserAccountSerializerVget
        elif self.request.version == 'v1':
            return UserAccountSerializerV1
        return UserAccountSerializer

    queryset = User.objects.all()
    # permission_classes = (IsSuperUser,)
    authentication_classes = (TokenAuthentication,)

    def list(self, request):
        auth_user = request.user.has_perm("account_management.full_access_to_ums")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        if request.user.is_superuser:
            result = User.objects.all()
        else:
            result = User.objects.filter(username= request.user.username)
        try:
            serialized_data = NewUserSerializer(result, many=True)
            generated_serialized_data=JSONRenderer().render(serialized_data.data)
            generated_serialized_data_json = json.loads(generated_serialized_data)
            team_data=Team_members.objects.all()
            team_dataserialized=TeamMembersSerializerForEdit(team_data,many=True)
            generated_teamname=JSONRenderer().render(team_dataserialized.data)
            generated_teamname_json = json.loads(generated_teamname)

            for each_data in generated_serialized_data_json:
                for data in generated_teamname_json:
                    if data['user']['id']==each_data['id']:
                        each_data['teamname']=data['team']['team_name']
                    else:
                        pass      

                

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)
        response = {
            'result': generated_serialized_data_json
        }
        return Response(response)

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser:
            # print('-----------------', request.user.is_superuser)
            user_obj = User.objects.get(username=request.user)
            try:
                first_name = request.data.get('first_name', '')
                last_name = request.data.get('last_name', '')
                username = request.data['username']
                email = request.data.get('email', '')
                password = request.data.get('password', '')
                is_active = request.data.get('is_active', True)
                is_superuser = request.data.get('is_superuser', True)
                is_staff = request.data.get('is_staff', False)
                groups = request.data.get('groups', None) #mush be in list
                # message = validate_password(password)
                # print(bool(message))
                # print(message)
                # if bool(message[0]):
                #     response = {
                #         'message': message
                #     }
                #     return Response(response)

                user_data = User(first_name=first_name, last_name=last_name, username=username, password=password,
                                 email=email, is_superuser=is_superuser, is_staff=is_staff, is_active=is_active)

                user_data.set_password(user_data.password)
                user_data.save()

                user_activity = UserActivity(user=user_data)
                user_activity.save()
                # group = request.data.get('groups', None)
                user_data.groups.add(*groups)
                response = {
                    'message': 'User Created Successfully',
                    'status': True,
                    'result': request.data
                }
                return Response(response, status=status.HTTP_201_CREATED)
            except Exception as ex:
                response = {
                    'message': str(ex)
                }
                return Response(response)

        else:
            response = {
                'message': 'Only Admin Can Create Users'
            }
            return Response(response)

    def update(self, request, *args, **kwargs):
        print(kwargs['pk'])
        print(request.data)
        if request.user.is_superuser:

            try:
                user = User.objects.get(id=kwargs['pk'])
                first_name = request.data['first_name']
                last_name = request.data['last_name']
                username = request.data['username']
                email = request.data['email']
                groups = request.data['groups']
                is_superuser = request.data['is_superuser']
                is_staff = request.data['is_staff']
                is_active = request.data['is_active']
                user.groups.clear()
                user.groups.add(*groups)
                # if groups:
                #     group_obj = Group.objects.get(name=groups)
                #     user.groups.add(group_obj)
                user_obj = User.objects.filter(id=kwargs['pk'])

               
                user_activity = UserActivity.objects.filter(user=user_obj.first()).first()
                if is_active:
                    user_activity.date = datetime.datetime.now()
                    user_activity.block_count = 0
                    user_activity.save()
                # user_profile = UserActivity.objects.get(user_id=username_exist.first())

                user_obj.update(first_name=first_name, last_name=last_name, username=username, email=email,
                                is_superuser=is_superuser, is_staff=is_staff, is_active=is_active)
                response = {
                    'message': 'successfully Updated'
                }

            except Exception as error:
                response = {
                    'message': str(error)
                }
                return Response(response)

            return Response(response)
            # return JsonResponse({'Successfully updated': request.data}, safe=False)
        else:
            response = {
                'message': 'Only Admin can Update User Info'
            }
            return Response(response)

    def update_one_time_password(self, request):

        username = request.data['new_username']
        password = request.data['new_password']
        confirm_password = request.data['confirm_password']

        # message = validate_password(password)
        # if len(message) > 0:
        #     response = {
        #         'password_errors': message
        #     }
        #     return Response(response)
        #
        # if password != confirm_password:
        #     response = {
        #         'message': 'Password and Confirm Password does not match'
        #     }
        #     return Response(response)

        user_obj = User.objects.get(username=username)
        user_obj.set_password(password)
        user_obj.save()
        login_record = UserActivity.objects.filter(user_id=user_obj.id)
        login_record.update(otp_expired=True)
        response = {
            'message': 'Password Updated successfully',
        }
        return Response(response, status=status.HTTP_200_OK)


    @action(detail=True, methods=['POST'])
    def changePassword(self, request):
        """
        An endpoint for changing password.
        """
        # permission_classes = (permissions.IsAuthenticated, )


        # if request.user.is_superuser == False:
        #     return Response({"message": "sorry only Superuser can change password"})

        serializer = ChangePasswordSerializer(data=request.data)

        if serializer.is_valid():
            user_id = serializer.data.get("user_id")
            user = User.objects.filter(id=user_id)
            if user:
                user[0].set_password(serializer.data.get("new_password"))
                user[0].save()

                if UserActivity.objects.filter(user=user[0]).exists() == False:
                    UserActivity(user=user[0]).save()

                user_activity = UserActivity.objects.get(user=user[0])
                print("user_activity--------",user_activity.otp_expired)
                user_activity.otp_expired = False
                user_activity.save()
                # login_record.update(otp_expired=True)

                response = {
                    'message': 'Password Updated successfully',
                }
                return Response(response,status=status.HTTP_204_NO_CONTENT)
            else:
                return Response("user not avaliable", status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AccountDeactivate(viewsets.ViewSet):

    permission_classes = [permissions.AllowAny]

    def de_activate_account(self, request):
        try:

            username = request.data['username']

            user = User.objects.filter(username=username).first()

            if user.is_superuser == False:
                user.is_active=False

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'message': 'You have only three attempts, your account has been deactivated'
        }
        return Response(response)


class AddedUsers(ModelViewSet):
    """
    return the count of users added in group
    """
    queryset = User.objects.all()
    serializer_class = UserAccountSerializerV1
    authentication_classes = (TokenAuthentication,)
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        return JsonResponse({"details": "Only retrieve data allowed"})

    def retrieve(self, request, *args, **kwargs):
        try:
            self.queryset = User.objects.filter(groups__name=self.kwargs['pk'])
            print(self.queryset)
        except:
            return JsonResponse({"NO Users": "NO users found"})

        return JsonResponse({"AddedUsers": self.queryset.count()})


class ChosenUser(ModelViewSet):
    """
    Return the total users added in a group
    """
    queryset = User.objects.all()
    authentication_classes = (TokenAuthentication,)
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        return JsonResponse({"permission": "You are only allowed to retrieve data"})

    def retrieve(self, request, *args, **kwargs):
        try:
            self.queryset = User.objects.filter(groups__id=self.kwargs['pk'])
            data = UserAccountSerializer(self.queryset, many=True)
        except:
            return JsonResponse({"Failed": "No data found"}, safe=False)

        return JsonResponse(data.data, safe=False)


class AddGroupViewSet(ModelViewSet):
    """
    perform all operations related to group
    """

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1' and self.action == 'list':
            return GroupSerializer
        elif self.action == 'retrieve':
            return GroupSerializer
        return GroupSerializers

    # permission_classes = (IsSuperUser,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        self.queryset = Group.objects.all()
        return self.queryset

    def list(self, request, *args, **kwargs):
        auth_user = request.user.has_perm("account_management.full_access_to_ums")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        users_in_group = []
        try:

            group_obj = Group.objects.all()
            serialized_data = GroupSerializers(group_obj, many=True)
            group_obj = Group.objects.all()
            main_data = GroupSerializer(group_obj, many=True)

            return Response(main_data.data)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

    def group_info(self, request):
        auth_user = request.user.has_perm("account_management.full_access_to_ums")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        users_in_group = []
        if request.user.is_superuser:
            groups = Group.objects.all()
            for i in groups:
                users_count = {}
                id = i.id
                group_count = User.objects.filter(groups=id).count()
                group_name = Group.objects.get(id=id)
                users_count['id'] = group_name.id
                users_count['name'] = group_name.name
                users_count['total_users'] = group_count
                # count = count + 1
                users_in_group.append(users_count)
        # print(users_in_group)

        return Response({'result': users_in_group})

    def create(self, request, *args, **kwargs):
        if request.user.is_superuser or request.user.has_perm("account_management.full_access_to_ums") :

            try:
                print(request.data)
                add_group = Group(name=request.data['group'])
                add_group.save()
                print(request.data['group'])
                permission = request.data['permisions']
                add_group.permissions.add(*permission)
                print("done")
            except:
                return JsonResponse({"Failed": "creation of data failed"})

            return JsonResponse({"success": "Data created successfully"})
        else:
            response = {
                'message': 'Only Admin Can Create Custom Groups'
            }
            return Response(response)

    def update(self, request, *args, **kwargs):
        auth_user = request.user.has_perm("account_management.full_access_to_ums")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        print(kwargs['pk'], "id")
        print(request.data, "data")
        if request.user.is_superuser:

            try:
                print(kwargs['pk'], "id")
                print(request.data, " data")
                add_group = Group.objects.get(id=kwargs['pk'])
                add_group.name = request.data['groupname']
                permisson = request.data['permissions']
                add_group.permissions.clear()
                # add_group.user_set.clear()
                # user = request.data['groupUsers']
                # add_group.user_set.add(*user)
                add_group.permissions.add(*permisson)
                add_group.save()
                print("saved")
            except:
                return JsonResponse({"Failed": "Data updating failed"})

            return JsonResponse({"success": "Data updated successfully"})

        else:
            response = {
                'message': 'Only Admin can Update Group Info'
            }
            return Response(response)

    @action(detail=True, methods=['POST'])
    def all_user_of_group(self, request):
        try:
            group_name = request.data['group_name']
            group = Group.objects.get(name=group_name)
            users = group.user_set.all().values('id', 'username')
            response = {
                'message': 'Group users',
                "result":users
            }
            return Response(response)
        except Exception as e:
            response = {
                'message': "can not get '{}' group user".format(group_name),
                "error":str(e)
            }
            return Response(response)


    
    @action(detail=True, methods=['POST'])
    def edit_user_of_group(self, request):
        try:
            group_name = request.data['group_name']
            group_users = request.data['group_users']
            group = Group.objects.get(name=group_name)
            group.name = group_name
            group.user_set.clear()
            group.user_set.add(*group_users)
            group.save()
            # users = group.user_set.all().values('id', 'username')
            response = {
                'message': "Successfully edit",
                # "result": users
            }
            return Response(response)
        except Exception as e:
            response = {
                'message': "Unsuccessful Edit",
                "error": str(e)
            }
            return Response(response)

class ViewPermissions(viewsets.ViewSet):
    """
    list all the permissions data
    """
    serializer_class = PermissionSerializer
    queryset = Permission.objects.all()
    authentication_classes = (TokenAuthentication,)

    def list(self, request):
        auth_user = request.user.has_perm("account_management.full_access_to_ums")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        try:
            queryset = Permission.objects.all()
            serialized = PermissionSerializer(queryset, many=True)
            response = {
                'result': serialized.data
            }
            return Response(response)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)


class TeamView(viewsets.ModelViewSet):
    """
    Team view API viewset

    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    authentication_classes = (TokenAuthentication,)

    def list(self, request, *args, **kwargs):
        queryset = Team.objects.all()
        serializer = TeamSerializer(queryset, many=True)
        return Response({"results":serializer.data})

    def create(self, request, *args, **kwargs):
        try:
            user = User.objects.get(id=request.data['team_leader'])
            if user.groups.filter(name='TMO').exists():
                lead_check = Team.objects.filter(team_leader=user.id)
                if Team.objects.filter(team_leader=user.id).exists():
                    return Response({'message':"'{0}' is already a leader of  team '{1}'".format(user.username, lead_check[0].team_name)}, status=status.HTTP_201_CREATED)

                    # if len(lead_check)==0:
                    #     list_of_user.append(UserAccountTMO(user).data)
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response({'message':"Team created Successfully"}, status=status.HTTP_201_CREATED, headers=headers)
            else:
                return Response({'message':"user dont have TMO permission"})
        except Exception as e:
            print("exceptions ",e)
            return Response({'Error':"user have not premissiona:  {0}".format(e)})

                
    @action(detail=True, methods=['GET'])
    def list_of_TMO(self, request):
        """this list of all user have the TMO permission and
         if the user want to be a Leader he can become one
        """
        list_of_user = []
        if request.user.is_superuser:
            users = User.objects.filter(is_active=True)
            
            for user in users:

                if user.groups.filter(name='TMO').exists():
                    list_of_user.append(UserAccountTMO(user).data)
                    # lead_check = Team.objects.filter(team_leader=user.id)

                    # if len(lead_check)==0:
                    #     list_of_user.append(UserAccountTMO(user).data)
            return Response(list_of_user)

        elif request.user.groups.filter(name='TMO').exists():
            lead_check = Team.objects.filter(team_leader=request.user.id)

            if lead_check:
                return Response("sorry you are part of Team: {0}".format(lead_check[0].team_name))
            list_of_user.append(UserAccountTMO(request.user).data)
            return Response(list_of_user)
        else:
            return Response("sorry you cannot create Team")


class TeamMemmberView(viewsets.ModelViewSet):
    """
    Team view API viewset

    """
    queryset = Team_members.objects.all()
    serializer_class = TeamMembersSerializer
    authentication_classes = (TokenAuthentication,)


    def create(self, request, *args, **kwargs):
        print("user Team uer ", request.data['user'])
        try:
            user = User.objects.get(id=request.data['user'])
            print(user)
            print(user.groups.filter(name='TMO').exists())
            if user.groups.filter(name='TMO').exists() or user.is_superuser:
                return Response({"message":"team member user is a superuser or a TMO user"})
            else:
                serializer = self.get_serializer(data=request.data)
                serializer.is_valid(raise_exception=True)
                self.perform_create(serializer)
                headers = self.get_success_headers(serializer.data)
                return Response("Memeber Successfully added", status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print("exceptions ",e)
            return Response("user have not premission {}".format(e))


    @action(detail=True, methods=['POST'])
    def create_bulk(self, request, *args, **kwargs):
        # print("user Team uer ", request.data['user'])
        try:

            users = request.data['users']
            team_id = request.data['team']
            team = Team.objects.get(id=team_id)
            list_of_teamMember = []
            for user_id in users:
                user = User.objects.get(id=user_id)
                print(user)

                # print(user.groups.filter(name='TMO').exists())
                if user.groups.filter(name='TMO').exists() or user.is_superuser:
                    response = {
                        "message": "team member '{0}' is a superuser or a TMO user".format(user.username)
                    }
                    return Response(response)
                else:
                    if Team_members.objects.filter(user = user).exists():
                        response = {
                            "message": "user '{0}' is already part of another team".format(user.username)
                        }
                        return Response(response)

                    list_of_teamMember.append(Team_members(team = team, user = user))
                    # serializer = self.get_serializer(data=request.data)
                    # serializer.is_valid(raise_exception=True)
                    # self.perform_create(serializer)
                    # headers = self.get_success_headers(serializer.data)
                
            Team_members.objects.bulk_create(list_of_teamMember)
            return Response("Memeber Successfully added", status=status.HTTP_201_CREATED)
        except Exception as e:
            print("exceptions ",e)
            return Response("user have not premission {}".format(e))


    @action(detail=True, methods=['POST'])
    def get_team_and_members(self, request,  *args, **kwargs):
        try:
            

            team_and_member = {}
            id = kwargs['id']
            
            team = Team.objects.get(id=id)
            list_of_members = []
            # team_value = 
            team_and_member['id'] = team.id
            team_and_member['team_name'] = team.team_name
            team_and_member['description'] = team.description
            team_and_member['team_leader_id'] = team.team_leader.id
            team_and_member['team_leader_name'] = team.team_leader.username
            team_and_member['id'] = team.id

            team_member = Team_members.objects.filter(team = team)
            for each_memeber in team_member:
                
                each_user = {}
                each_user['id'] = each_memeber.user.id
                each_user['username'] = each_memeber.user.username
                try:
                    each_user['user_group'] = each_memeber.user.groups.first().name 
                except:
                    each_user['user_group'] = None
                list_of_members.append(each_user)
                
            team_and_member['team_member'] = list_of_members
            # serializer = TeamMembersSerializerForEdit(team_member, many=True)
            # print(serializer.data)
            return Response({"result":team_and_member})
            
        except Exception as e:
            print("Exception --> ",e)
            return Response({"error":str(e)})

    @action(detail=True, methods=['POST'])
    def update_bulk(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                id = kwargs['id']
                team_name = request.data['team_name']
                description = request.data['description']
                team_leader_id = request.data['team_leader_id']
                team_members = request.data['team_members']

                team = Team.objects.get(id=id)

                team.team_name = team_name
                team.description = description
                # team.team_leader = User.objects.get(id= team_leader_id)
                team.team_leader = User.objects.get(id=team_leader_id)

                new_member = set(team_members)
                old_member = set([user['user'] for user in Team_members.objects.filter(team = team).values('user')])

                print("ignore",old_member.intersection(new_member))
                print("remove",old_member.difference(new_member))
                print("add",new_member.difference(old_member))


                add_user = new_member.difference(old_member)

                remove_user = old_member.difference(new_member)
                
                list_of_teamMember = []
                for user_id in add_user:
                    user = User.objects.get(id=user_id)
                    print(user)

                    if user.groups.filter(name='TMO').exists() or user.is_superuser:
                        return Response({"message":"team member user is a superuser or a TMO user"})

                    else:
                        list_of_teamMember.append(Team_members(team = team, user = user))

                Team_members.objects.bulk_create(list_of_teamMember)

                for user_id in remove_user:
                    team_member_delete = Team_members.objects.get(user = user_id)
                    print(team_member_delete)
                    team_member_delete.delete()

                team.save()

            return Response({"message":"Updated Successfully"})
        except Exception as e:
            print("Exception --> ",e)
            return Response({"error":str(e)})


    @action(detail=True, methods=['GET'])
    def list_of_TAO_other(self, request):
        """this function will return all the TMO and 
        other user which are not in any TMO team
        """
        list_of_user = []
        if request.user.is_superuser:
            users = User.objects.filter(is_active=True)
            
            for user in users:

                if user.groups.filter(~Q(name="TMO")).exists():
                    member_check = Team_members.objects.filter(user=user.id)

                    if len(member_check)==0:
                        list_of_user.append(UserAccountTMO(user).data)
            return Response(list_of_user)


        # elif request.user.groups.filter(name='TMO').exists():
        #     lead_check = Team.objects.filter(team_leader=request.user.id)
            
        #     if lead_check:
        #         return Response("sorry you are part of Team: {0}".format(lead_check[0].team_name))
        #     list_of_user.append(UserAccountTMO(request.user).data)
        #     return Response(list_of_user)
        # else:
        #     return Response("sorry you cannot create Team")

class AccountSettingViewSet(ModelViewSet):
    """

    specific settings for the user

    """
    serializer_class = AccountSettingSerializers
    queryset = AccountSettings.objects.all()
    authentication_classes = (TokenAuthentication,)

    def list(self, request, *args, **kwargs):
        self.queryset = AccountSettings.objects.filter(user=request.user)
        data = AccountSettingSerializers(self.queryset, many=True)
        print(data.data)
        return Response({"result": data.data})

    def create(self, request, *args, **kwargs):
        try:
            account_setting = AccountSettings.objects.filter(user=request.user)
            print(len(account_setting))
            if len(account_setting) is 0:
                print(request.data, "in user data")
                user = User.objects.get(id=request.user.id)
                setting = AccountSettings(user=user, OCS=request.data['notifywhen'])
                setting.save()
                return Response({"Successfully Added": request.data})
            else:
                return Response({"Already exists": request.data})
        except Exception as e:
            print(e)
            return Response({"Unsuccessfull": request.data})

    def update(self, request, *args, **kwargs):
        try:
            print(kwargs['pk'])
            account = AccountSettings.objects.get(id=kwargs['pk'])
            account.OCS = kwargs['notifywhen']
            account.save()
        except Exception as e:
            return Response({'Failed to  update': request.data})
        return Response({'Successfully updated': request.data})


class AddUserProfileViewSet(ModelViewSet):
    """
    create and edit the user profile
    """

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return UserProfileSerializer
        return UserProfileSerializer

    queryset = UserProfile.objects.all()
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return self.queryset.filter(
            user=self.request.user)

    def create_profile(self, request):
        if request.user.is_superuser :

            try:
                description = request.data['description']
                dob = request.data['date_of_birth']
                dob = datetime.datetime.fromtimestamp(float(dob) / 1000)
                employee_id = request.data['employee_id']
                # cnic = request.data['cnic']
                contact = request.data['contact']
                expire_on = request.data['expire_on']
                expire_on = datetime.datetime.fromtimestamp(float(expire_on) / 1000)
                address = request.data['address']
                user_id = request.data['user_id']
                user_obj = User.objects.get(id=user_id)
            except Exception as error:
                response = {
                    'Error': str(error)
                }
                return Response(response)

            try:

                UserProfile.objects.create(description=description, date_of_birth=dob, employee_id=employee_id,
                                           contact=contact, expire_on=expire_on, address=address, user=user_obj)
            except Exception as error:
                response = {
                    'Error': str(error)
                }
                return Response(response)

            response = {
                'message': 'User Created Successfully'
            }
            return Response(response)

        response = {
            'message': 'Only Admin can create User Profile'
        }
        return Response(response)

    def retrive_user(self, request,  *args, **kwargs):
        try:
            id = kwargs['id']
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        try:
            obj = UserProfile.objects.filter(user_id=id).values()
            group_obj = Group.objects.filter(user=id).values()
            print(group_obj)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)
        response = {
            'profile_info': obj,
            'groups': group_obj
        }
        return Response(response)

    def update_profile(self, request, *args, **kwargs):

        profile_id = kwargs['id']
        if request.user.is_superuser:

            try:
                profile_obj = UserProfile.objects.filter(id=profile_id).values()
            except Exception as error:
                response = {
                    'message': str(error)
                }
                return Response(response)

            try:
                # first_name = request.data['first_name']
                # last_name = request.data['last_name']
                address = request.data['address']
                employee_id = request.data['employee_id']
                description = request.data['description']
                date_of_birth = request.data['date_of_birth']
                date_of_birth = datetime.datetime.fromtimestamp(float(date_of_birth) / 1000)
                # cnic = request.data['cnic']
                contact = request.data['contact']

            except Exception as error:
                response = {
                    'message': str(error)
                }
                return Response(response)

            try:
                profile_obj.update(address=address,
                                   employee_id=employee_id, description=description,
                                   date_of_birth=date_of_birth, contact=contact)
            except Exception as error:
                response = {
                    'Error': str(error)
                }
                return Response(response)

            response = {
                'message': 'Updated Successfully'
            }
            return Response(response)
        response = {
            'message': 'Only Admin Can Update User Profile'
        }
        return Response(response)


class LoginView(APIView):
    permission_classes = (permissions.AllowAny,)

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return UserAccountSerializer
        return UserAccountSerializerV1

    def post(self, request):
        if 'username' in request.data:
            username = request.data['username']
        else:
            username = None

        if 'password' in request.data:
            password = request.data['password']
        else:
            password = None
        print(username)
        print(password)
        username_exist = User.objects.filter(username=username)
        if username_exist.exists() == False:
            response = {
                'message': 'No User Found!',
                'status': False,
                'result': None,

            }
            return Response(response) 

        user = authenticate(username=username, password=password)

        if user:
            try:
                user_obj = User.objects.get(username=username)
                # extra check because most of the old user done have UserActivity or 
                if UserActivity.objects.filter(user=user).exists() == False:
                    user_activity = UserActivity(user=user)
                    user_activity.save()
                user_profile = UserActivity.objects.get(user_id=user_obj.id)
                flag = user_profile.otp_expired
            except:
                flag = None

            serializer = self.get_serializer_class()
            result = serializer(instance=user).data

            if user_obj.is_superuser:
                type=[
                        {
                            "id": 0,
                            "name": "SUPERUSER"
                        }
                    ]
            else:
                user_group = User.objects.get(username=username)
                type = Group.objects.filter(user=user_group.id).values()

            result['token'] = Token.objects.get_or_create(user=user)[0].key
            response = {
                'message': 'User Logged In Successfully',
                'status': True,
                'result': result,
                'type': type,
                'flag': flag,
            }

            if UserProfile.objects.filter(user=user).exists() == False:
                ts = time.time()
                UserProfile.objects.create(user= user, first_name= user.first_name,
                last_name = user.last_name, employee_id = str(ts).replace(".",""))

            return Response(response)

        else:

            def getDuration(then, now = datetime.datetime.now()):

                # Returns a duration as specified by variable interval
                # Functions, except totalDuration, returns [quotient, remainder]

                duration = now - then # For build-in functions
                duration_in_s = duration.total_seconds() 
                
                def years():
                    return divmod(duration_in_s, 31536000) # Seconds in a year=31536000.
                
                def days(seconds = None):
                    return divmod(seconds if seconds != None else duration_in_s, 86400) # Seconds in a day = 86400

                def hours(seconds = None):
                    return divmod(seconds if seconds != None else duration_in_s, 3600) # Seconds in an hour = 3600

                def minutes(seconds = None):
                    return divmod(seconds if seconds != None else duration_in_s, 60) # Seconds in a minute = 60

                def seconds(seconds = None):
                    if seconds != None:
                        return divmod(seconds, 1)   
                    return duration_in_s

                y = years()
                d = days(y[1]) # Use remainder to calculate next variable
                h = hours(d[1])
                m = minutes(h[1])
                s = seconds(m[1]) 

                return {
                    'years': y,
                    'days': d,
                    'hours': h,
                    'minutes': m,
                    'seconds': s,
                }

            if UserActivity.objects.filter(user=username_exist.first()).exists() == False:
                user_activity = UserActivity(user=username_exist.first())
                user_activity.save()
            user_profile = UserActivity.objects.get(user_id=username_exist.first())
            # extra check because most of the old user done have UserActivity or 
            
            if user_profile.date == None:
                
                print("--------------------- if Date None -------------------\n\n\n")

                user_profile.date= datetime.datetime.now()
                user_profile.block_count = 1
                user_profile.save()
                print("empty")
                print("----------------------------------------\n\n\n")

            else:
                user = username_exist.first()
                if user.is_active:
                    then = user_profile.date
                    data_time_checker = getDuration(then)
                    # print(data_time_checker)

                    days = data_time_checker['days'][0]
                    hours = data_time_checker['hours'][0]
                    if days <= 0 and hours <= 5:
                        user_profile.block_count = user_profile.block_count + 1
                        user_profile.save()

                        if user_profile.block_count >=3:
                            user = username_exist.first() 
                            if user.is_superuser == False:
                                # print("yes its working ")
                                user.is_active = False
                                user.save()

                    else:
                        user_profile.date= datetime.datetime.now()
                        user_profile.block_count = 1
                        user_profile.save()
                    response = {
                        'message': 'Wrong Password!',
                        'status': False,
                        'result': None
                    }
                    return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)
                else:
                    response = {
                        'message': 'User is blocked',
                        'status': False,
                        'result': None
                        }   
                    return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)

                
            response = {
                'message': 'Wrong Password!',
                'status': False,
                'result': None
            }
            return JsonResponse(response, status=status.HTTP_400_BAD_REQUEST)


class LogoutView(APIView):
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def post(self, request):
        user = request.user
        print(user)
        Token.objects.filter(user=user).delete()

        response = {
            'message': 'User Logged Out Successfully',
            'status': True,
            'result': None
        }
        return JsonResponse(response)
