from target_management.ess_controller import EssApiController
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from .models import AvatarPostAction, AvatarReactionAction, AvatarCommentAction, AvatarMessageAction, AddAccount,\
                    AvatarProfile, AvatarShareAction, AvatarAddFriendAction
from .serializers import AddAccountSerializer, AvatarProfileSerializer, AvatarMessageSerializer, AvatarPostSerializer,\
                         AvatarReactionSerializer, AvatarShareSerializer, AvatarCommentSerializer, SocialReloginSerializer
from core_management.models import FakeIdentity
import datetime
import json
from case_management.views import perform_upload

from avatar_management import serializers
# Create your views here.

ess_obj = EssApiController()


def date_change(date):
    return datetime.datetime.fromtimestamp(float(date) / 1000)


class Avatar(viewsets.ViewSet):

    authentication_classes = (TokenAuthentication,)

    def add_profile(self, request):
        print(request.data)
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        email = request.data.get('email', '')
        phone_number = request.data.get('phone_number', '')
        nationality = request.data.get('nationality', '')
        address = request.data.get('address', '')
        religion = request.data.get('religion', '')
        martial_status = request.data.get('martial_status', '')
        date_of_birth = request.data.get('date_of_birth', '')
        date_of_birth = date_change(date_of_birth)
        try:
            AvatarProfile.objects.create(first_name=first_name, last_name=last_name, email=email,
                                         phone_number=phone_number, nationality=nationality, address=address,
                                         religion=religion, martial_status=martial_status,
                                         date_of_birth=date_of_birth)
        except Exception as error:
            response = {
                'message': 'Error',
                'result': str(error)
            }
            return Response(response, status=status.HTTP_200_OK)

        response = {
            'message': 'Profile added successfully',
            'status': True,
        }
        return Response(response, status=status.HTTP_200_OK)

    def all_profiles(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        try:
            profiles = AvatarProfile.objects.all()
            serialized_profiles = AvatarProfileSerializer(profiles, many=True)
            if not profiles:
                response = {
                    'message': 'No Profiles'
                }
                return Response(response, status=status.HTTP_200_OK)
        except Exception as error:
            response = {
                'message': 'No Profiles Found',
                'status': False,
                'result': str(error)
            }
            return Response(response, status=status.HTTP_200_OK)

        return Response(serialized_profiles.data)

    def fetch_profiles(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        id = request.data['id']

        try:
            obj = AvatarProfile.objects.filter(id=id).values()
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)
        response = {
            'result': obj
        }

        return Response(response)

    def update_profile(self, request, *args, **kwargs):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        profile_id = kwargs['pk']
        try:
            avatar_profile_obj = AvatarProfile.objects.filter(id=profile_id).values()
        except Exception as error:
            response = {
                'message': "Profile Doesn't Exist",
                'result': str(error)
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)

        if request.data is not None:
            try:
                first_name = request.data['first_name']
                last_name = request.data['last_name']
                email = request.data['email']
                phone_number = request.data['phone_number']
                nationality = request.data['nationality']
                address = request.data['address']
                religion = request.data['religion']
                martial_status = request.data['martial_status']
                date_of_birth = request.data['date_of_birth']
                converted_date = date_change(date_of_birth)
                avatar_profile_obj.update(first_name=first_name, last_name=last_name, email=email,
                                          phone_number=phone_number, nationality=nationality, address=address,
                                          religion=religion, martial_status=martial_status,
                                          date_of_birth=converted_date)

                response = {
                    'message': 'Profile Updated'
                }

                return Response(response, status=status.HTTP_200_OK)
            except Exception as error:

                response = {
                    'message': 'Error in updating profile',
                    'result': str(error)
                }
                return Response(response, status=status.HTTP_200_OK)

    def delete_profile(self, request, *args, **kwargs):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        profile_id = kwargs['pk']
        try:
            avatar_profile_obj = AvatarProfile.objects.filter(id=profile_id)
            avatar_profile_obj.delete()
            response = {
                'message': 'Profile Deleted'
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as error:
            response = {
                'message': "Profile doesn't Exist",
                'result': str(error)
            }
            return Response(response, status=status.HTTP_204_NO_CONTENT)

    def add_account(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        if request.data is not None:
            username = request.data['username']
            password = request.data['password']
            social_media = request.data['social_media']
            email = request.data['email']
            friends_list = "[]"

            try:
                accounts = AddAccount.objects.filter(username=username)
                for users in accounts:
                    if users.social_media == social_media:
                        response = {
                            'message': 'Account already exist'
                        }
                        return Response(response, status=status.HTTP_200_OK)

            except Exception as error:
                response = {
                    'message': str(error)
                }
                return Response(response)
            try:
                AddAccount.objects.create(username=username, password=password, social_media=social_media, created_by=request.user, email=email, friends_list="[]",friends_groups='[]')
            except Exception as error:
                response = {
                    "message": "Account Creation Failure",
                    "status": False,
                    'result': str(error)
                }
                return Response(response, status=status.HTTP_202_ACCEPTED)
        response = {
            "message": "Account Added Successfully",
            "status": True,
        }
        return Response(response, status=status.HTTP_200_OK)

    def delete_account(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        id = request.query_params.get('id')
        account = AddAccount.objects.filter(id = id).first()
        data = account.username + ": " + account.social_media
        account.delete()
        return Response({"message":"id {0} {1} deleted".format(id, data)})
    # def success_rate(self,request,**kwargs):
    #     try:
    #         list_for_request=[]
    #         id=kwargs['id']
    #         friend=AddAccount.objects.filter(id=id).first()
    #         friend_list_json = json.loads(friend.friends_list)
    #         counting_friend_request=AvatarAddFriendAction.objects.filter(account=id)
    #         for data in counting_friend_request:
    #             list_for_request.append(data.target_username)
    #         no_friend_request=len(set(list_for_request))       
    #         unique_list=set(list_for_request)
    #         count=0
    #         for each_name in unique_list:
    #             for each_data in friend_list_json:
    #                 if each_name== each_data['username']:
    #                     count=count+1
    #                 else:
    #                     pass
    #         percentage=(count/no_friend_request)*100         

    #     except Exception as error:
    #         response = {
    #             "message": error,
    #             "status": True,
    #             'result': str(error)
    #             }
    #         return Response(response, status=status.HTTP_202_ACCEPTED)
    #     response = {
    #         "success_rate": percentage
    #     }
    #     return Response(response, status=status.HTTP_200_OK)
    def all_accounts(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': []
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        try:
            if request.user.is_superuser :
                accounts = AddAccount.objects.all()
            else:
                username = request.user.username
                accounts = AddAccount.objects.filter(created_by=username)

            serialized_accounts = AddAccountSerializer(accounts, many=True)
            if not accounts:
                # response = {
                #     'message': 'No accounts',
                #     'status': False,
                #     'result': []
                # }
                return Response([], status=status.HTTP_200_OK)
        except Exception as error:
            response = {
                'message': 'Error',
                'result': [error]
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serialized_accounts.data)

    def post_avatar_action(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        if request.data is not None:
            request.data._mutable = True
            post_text = request.data['post_text']
            post_date = request.data['post_date']
            added_account = request.data['account']
            request.data['image_url'] = ""
            # converted_date = datetime.datetime.fromtimestamp(float(post_date)/1000)
            data = {}
            data['image_url'] = ""
            print("image-------", request.data['image'] )
            account = AddAccount.objects.get(id=added_account)

            if request.data['image'] != "null" :
                data = perform_upload(request.data, 'image')
            else:
                print("image not found")
                if account.social_media == "Instagram":
                
                    response = {
                            'message': 'image is required for Instagram',
                            'status': False,
                            'result': []
                        }
                    return Response(response, status=status.HTTP_200_OK)
                
            converted_date = date_change(post_date)
            try:
                account = AddAccount.objects.get(id=added_account)
                username = account.username
                password = account.password
                social_media = account.social_media
                AvatarPostAction.objects.create(post_text=post_text,
                                                post_date=converted_date,
                                                account=account,
                                                image_url=data['image_url'],
                                                created_by=request.user)

                try:
                    if "Linkedin" == account.social_media :
                        ess_response = ess_obj.action_post(post_text, social_media, account.email, password, data['image_url'])
                    else:

                        ess_response = ess_obj.action_post(post_text, social_media, username, password, data['image_url'])

                except Exception as error:
                    response = {
                        'message': 'No Response',
                        'status': False,
                        'result': str(error)
                    }
                    return Response(response, status=status.HTTP_200_OK)

                response = {
                    'message': "Added post action",
                    'status': True,
                }
                return Response(response)
            except Exception as error:
                response = {
                    'message': "Added account error",
                    'status': False,
                    'result': error
                }
                return Response(response)


    def comment_avatar_action(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        if request.data is not None:
            comment_text = request.data['comment_text']
            target_post_url = request.data['post_url']
            comment_date = request.data['comment_date']
            added_account = request.data['account']
            converted_date = date_change(comment_date)
            try:
                account = AddAccount.objects.get(id=added_account)
                username = account.username
                password = account.password
                social_media = account.social_media

            except Exception as error:
                response = {
                    'message': 'Added Account error',
                    'result': str(error)
                }
                return Response(response, status=status.HTTP_200_OK)

            AvatarCommentAction.objects.create(comment_text=comment_text,
                                               target_post_url=target_post_url,
                                               comment_date=converted_date,
                                               account=account,
                                               created_by=request.user)
            try:
                
                if account.social_media == "Facebook" or account.social_media == "Linkedin" or account.social_media == "Twitter":
                    username =  account.email
                    ess_response = ess_obj.action_comment(comment_text, target_post_url, social_media, username, password)
                else:
                    ess_response = ess_obj.action_comment(comment_text, target_post_url, social_media, username, password)

            except Exception as error:
                response = {
                    'result': error,
                    'status': False,
                    'message': "Microcrowler exception"
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            response = {

                'message': ess_response['message'],
                'status': True,
                'result': ess_response
            }
            return Response(response, status=status.HTTP_200_OK)
        response = {
                    'message': 'Proper data not provided',
                    'status': False,
                }
        return Response(response, status=status.HTTP_204_NO_CONTENT)

    def reaction_avatar_action(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        if request.data is not None:
            reaction_type = request.data['reaction_type']
            target_post_url = request.data['post_url']
            reaction_date = request.data['reaction_date']
            added_account = request.data['account']
            converted_date = date_change(reaction_date)
            try:
                account = AddAccount.objects.get(id=added_account)
                username = account.username
                password = account.password
                social_media = account.social_media

            except Exception as error:
                response = {
                    'message': 'Added Account error'
                }
                return Response(response, status=status.HTTP_204_NO_CONTENT)

            AvatarReactionAction.objects.create(reaction_type=reaction_type,
                                                target_post_url=target_post_url,
                                                reaction_date=converted_date,
                                                account=account,
                                                created_by=request.user)
            try:
                if account.social_media == "Facebook" or account.social_media == "Linkedin" or account.social_media == "Twitter":
                    username = account.email
                    ess_response = ess_obj.action_reaction(reaction_type, target_post_url, social_media, username, password)
                else:
                    ess_response = ess_obj.action_reaction(reaction_type, target_post_url, social_media, username, password)
            except Exception as error:
                response = {
                    'message': "Microcrowler exception",
                    'status': False,
                    'result': error
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            response = {
                'message': ess_response['message'],
                'status': True,
                'result':ess_response,
            }
            return Response(response, status=status.HTTP_200_OK)

        response = {
            'message': "No Request",
        }

        return Response(response, status=status.HTTP_204_NO_CONTENT)

    def message_avatar_action(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        if request.data is not None:
            try:
                title = request.data['title']
                description = request.data['description']
                message_text = request.data['message_text']
                target_username = request.data['target_username']
                message_date = request.data['message_date']
                added_account = request.data['account']
                converted_date = date_change(message_date)
            except Exception as error:
                print(error)
            try:
                account = AddAccount.objects.get(id=added_account)
                username = account.username
                password = account.password
                social_media = account.social_media

            except Exception as error:
                response = {
                    'message': 'Added Account error',
                    'result': str(error)
                }
                return Response(response, status=status.HTTP_204_NO_CONTENT)

            AvatarMessageAction.objects.create(title=title,
                                               description=description,
                                               message_text=message_text,
                                               target_username=target_username,
                                               message_date=converted_date,
                                               account=account,
                                               created_by=request.user)

            try:
                if account.social_media == "Facebook" or account.social_media == "Linkedin" or account.social_media == "Twitter":
                    username = account.email
                    ess_response = ess_obj.action_send_message(social_media, target_username, message_text, username,
                                                           password)
                else:
                    ess_response = ess_obj.action_send_message(social_media, target_username, message_text, username,
                                                           password)

            except Exception as error:
                response = {
                    'message': "MicroCrowler exception",
                    'status': False,
                    'result': error
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            response = {
                'message': ess_response['message'],
                'status': True,
                'result': ess_response
            }
            return Response(response, status=status.HTTP_200_OK)

        response = {
            'message': "No Request",
        }

        return Response(response, status=status.HTTP_204_NO_CONTENT)

    def share_avatar_action(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        if request.data is not None:
            try:
                share_text = request.data['share_text']
                target_post_url = request.data['post_url']
                share_date = request.data['share_date']
                added_account = request.data['account']
                converted_date = date_change(share_date)

            except Exception as error:
                response = {
                    'message': 'Arguments Error'
                }
                return Response(response)

            try:
                account = AddAccount.objects.get(id=added_account)
                username = account.username
                password = account.password
                social_media = account.social_media

            except Exception as error:
                response = {
                    'message': 'Added Account error'
                }
                return Response(response, status=status.HTTP_204_NO_CONTENT)

            AvatarShareAction.objects.create(post_text=share_text,
                                             target_post_url=target_post_url,
                                             share_date=converted_date,
                                             account=account,
                                             created_by=request.user)

            try:
                if account.social_media == "Facebook" or account.social_media == "Linkedin" or account.social_media == "Twitter":
                    username = account.email
                    ess_response = ess_obj.action_share(share_text, target_post_url, social_media, username, password)
                else:
                    ess_response = ess_obj.action_share(share_text, target_post_url, social_media, username, password)


            except Exception as error:
                response = {
                    'message': "MicroCrowler exception",
                    'status': False,
                    'result':  error
                }
                return Response(response, status=status.HTTP_404_NOT_FOUND)

            response = {
                'message': ess_response['message'],
                'status': True,
                'result': ess_response
            }
            return Response(response, status=status.HTTP_200_OK)

        response = {
            'message': "No Request",
        }

        return Response(response, status=status.HTTP_204_NO_CONTENT)

    def addfriend_avatar_action(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        try:
            target_username = request.data['username']
            action_date = request.data['action_date']
            added_account = request.data['account']
            target_type = request.data['target_type']
            action_date = date_change(action_date)
        except Exception as error:
            response = {
                'message': 'Arguments Error'
            }
            return Response(response)


        try:
            account = AddAccount.objects.get(id=added_account)
            username = account.username
            password = account.password
            social_media = account.social_media

            AvatarAddFriendAction.objects.create(account=account, target_username=target_username,
                                                 action_date=action_date, target_type=target_type,
                                                 created_by=request.user)

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        try:
            if account.social_media == "Facebook" or account.social_media == "Linkedin" or account.social_media == "Twitter":
                username = account.email

                ess_response = ess_obj.action_add_friend(social_media, username, target_username, password, target_type)

            else:
                ess_response = ess_obj.action_add_friend(social_media, username, target_username, password, target_type)

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'message': str(ess_response),
        }
        return Response(response)

    def update_avatars(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        if not request.data:
            response = {
                'message': 'Empty Request Data'
            }
            return Response(response)
        try:
            if 'friends_following' in request.data:
                username = request.data['email']
                friends = request.data['friends_following']
                social_media = request.data['social_media']

                account = AddAccount.objects.filter(email=username, social_media=social_media).values()

                account.update(friends_list=friends)
            elif 'status' in request.data:
                account_status = request.data['status']
                username = request.data['email']
                social_media = request.data['social_media']
                if account_status == '0':
                    final_status = False
                if account_status == '1':
                    final_status = True
                account = AddAccount.objects.filter(email=username, social_media=social_media).values()

                account.update(status=final_status)
            elif 'groups' in request.data:
                username = request.data['email']
                friends_groups = request.data['groups']
                social_media = request.data['social_media']

                account = AddAccount.objects.filter(email=username, social_media=social_media).values()
                account.update(friends_groups=friends_groups)

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'message': 'Account Updated'
        }
        return Response(response)

    def schedule_actions_archive(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        try:
            messages_details = AvatarMessageAction.objects.all()
            post_details = AvatarPostAction.objects.all()
            share_details = AvatarShareAction.objects.all()
            reaction_detail = AvatarReactionAction.objects.all()
            comment_detail = AvatarCommentAction.objects.all()

            serialized_messages_details = AvatarMessageSerializer(messages_details, many=True)
            serialized_post_details = AvatarPostSerializer(post_details, many=True)
            serialized_share_details = AvatarShareSerializer(share_details, many=True)
            serialized_reaction_details = AvatarReactionSerializer(reaction_detail, many=True)
            serialized_comment_detail = AvatarCommentSerializer(comment_detail, many=True)

            response = {
                'message_action_details': serialized_messages_details.data,
                'post_action_details': serialized_post_details.data,
                'share_action-details': serialized_share_details.data,
                'reaction_action_details': serialized_reaction_details.data,
                'comment_action_detail': serialized_comment_detail.data
            }
            return Response(response, status=status.HTTP_200_OK)

        except Exception as error:
            response = {
                'error': str(error)
            }
            return Response(response)

    def dashboard(self, request):
        auth_user = request.user.has_perm("avatar_management.amu_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        action_stats = {}
        social_media = ['Facebook', 'Twitter', 'Linkedin', 'Youtube', 'Reddit', 'Instagram']
        social_media_stats = {}
        avatar_status = {"block":0,
                            "free":0,
                            "engaged":0}
        upcomming_task = {}
        final = []
        mature = 0
        immature = 0
        avatar_types = {}
        avatar_types_list = []
        total_avatars = 0
        user = request.user
        if request.user.is_superuser:
            post_count = AvatarPostAction.objects.all().count()
            comment_count = AvatarCommentAction.objects.all().count()
            share_count = AvatarShareAction.objects.all().count()
            reaction_count = AvatarReactionAction.objects.all().count()
        else:
            post_count = AvatarPostAction.objects.filter(created_by = user).count()
            comment_count = AvatarCommentAction.objects.filter(created_by = user).count()
            share_count = AvatarShareAction.objects.filter(created_by = user).count()
            reaction_count = AvatarReactionAction.objects.filter(created_by = user).count()

        action_stats['post'] = post_count
        action_stats['comment'] = comment_count
        action_stats['share'] = share_count
        action_stats['reaction'] = reaction_count

        for sm in social_media:
            if request.user.is_superuser:
                count = AddAccount.objects.filter(social_media=sm).count()
            else:
                count = AddAccount.objects.filter(social_media=sm, created_by= user.username).count()
            social_media_stats['Category'] = sm
            social_media_stats['value'] = count
            final.append(dict(social_media_stats))

        if request.user.is_superuser:
            all_accounts = AddAccount.objects.all()
        else:
            all_accounts = AddAccount.objects.filter(created_by= user.username)

        for a in all_accounts:
            total_avatars = total_avatars + 1
            date = (datetime.datetime.now().date() - a.created_on)/30

            if date.days > 3:
                mature = mature + 1

            else:
                immature = immature + 1

            if request.user.is_superuser:
                post_check=AvatarPostAction.objects.filter(account=a, post_date__gte=datetime.datetime.now())
                react_check=AvatarReactionAction.objects.filter(account=a, reaction_date__gte=datetime.datetime.now())
                comment_check=AvatarCommentAction.objects.filter(account=a, comment_date__gte=datetime.datetime.now())
                message_check=AvatarMessageAction.objects.filter(account=a, message_date__gte=datetime.datetime.now())
                share_check=AvatarShareAction.objects.filter(account=a, share_date__gte=datetime.datetime.now())
                addFriend_check=AvatarAddFriendAction.objects.filter(account=a, action_date__gte=datetime.datetime.now())
            else:
                post_check=AvatarPostAction.objects.filter(account=a, post_date__gte=datetime.datetime.now(), created_by = user)
                react_check=AvatarReactionAction.objects.filter(account=a, reaction_date__gte=datetime.datetime.now(), created_by = user)
                comment_check=AvatarCommentAction.objects.filter(account=a, comment_date__gte=datetime.datetime.now(), created_by = user)
                message_check=AvatarMessageAction.objects.filter(account=a, message_date__gte=datetime.datetime.now(), created_by = user)
                share_check=AvatarShareAction.objects.filter(account=a, share_date__gte=datetime.datetime.now(), created_by = user)
                addFriend_check=AvatarAddFriendAction.objects.filter(account=a, action_date__gte=datetime.datetime.now(), created_by = user)

            if post_check or react_check or comment_check or message_check or share_check or addFriend_check:
                avatar_status['engaged'] = avatar_status['engaged'] + 1

            else:
                avatar_status['free'] = avatar_status['free'] + 1

        if request.user.is_superuser:
            total_fake_ids = FakeIdentity.objects.all().count()
        else:
            total_fake_ids = FakeIdentity.objects.filter(created_by= user).count()

        avatar_types['name'] = 'mature'
        avatar_types['value'] = mature

        avatar_types_list.append(dict(avatar_types))

        avatar_types['name'] = 'immature'
        avatar_types['value'] = immature

        avatar_types_list.append(dict(avatar_types))

        

        if request.user.is_superuser:
            comments = AvatarCommentAction.objects.filter(comment_date__gte=datetime.datetime.now())
            post = AvatarPostAction.objects.filter(post_date__gte=datetime.datetime.now())
            reacts = AvatarReactionAction.objects.filter(reaction_date__gte=datetime.datetime.now())
            messages = AvatarMessageAction.objects.filter(message_date__gte=datetime.datetime.now())
            share = AvatarShareAction.objects.filter(share_date__gte=datetime.datetime.now())
            addfriend = AvatarAddFriendAction.objects.filter(action_date__gte=datetime.datetime.now())
        else:
            comments = AvatarCommentAction.objects.filter(comment_date__gte=datetime.datetime.now(), created_by = user)
            post = AvatarPostAction.objects.filter(post_date__gte=datetime.datetime.now(), created_by = user)
            reacts = AvatarReactionAction.objects.filter(reaction_date__gte=datetime.datetime.now(), created_by = user)
            messages = AvatarMessageAction.objects.filter(message_date__gte=datetime.datetime.now(), created_by = user)
            share = AvatarShareAction.objects.filter(share_date__gte=datetime.datetime.now(), created_by = user)
            addfriend = AvatarAddFriendAction.objects.filter(action_date__gte=datetime.datetime.now(), created_by = user)
        
        all_data = [ ]

        for each_comment in comments:
            message = {}
            message['message'] = "user "+ each_comment.account.username +" comment '" + each_comment.comment_text + "' on " + each_comment.target_post_url
            message['time'] = each_comment.comment_date
            all_data.append(message)

        for each_post in post:
            message = {}
            message['message'] = "user " + each_post.account.username  + " post " + each_post.post_text 
            message['time'] = each_post.post_date 
            all_data.append(message)

        for each_react in reacts:
            message = {}
            message['message'] = "React '" + each_react.reaction_type + "' on '" + each_react.target_post_url + "'"
            message['time'] = each_react.reaction_date 
            all_data.append(message)

        for each_message in messages:
            message = {}
            message['message'] = each_message.account.username + " send message '" + each_message.message_text + "'"
            message['time'] = each_message.message_date 
            all_data.append(message)

        for each_share in share:
            message = {}
            message['message'] = each_share.account.username + " share " + each_share.post_text + " on " + each_share.target_post_url
            message['time'] = each_share.share_date 
            all_data.append(message)

        for each_addfriend in addfriend:
            message = {}
            message['message'] = each_addfriend.account.username + " add friend " + each_addfriend.target_username
            message['time'] = each_addfriend.action_date 
            all_data.append(message)
        


        #count block avatar
        if request.user.is_superuser:
            avatar_status['block'] = AddAccount.objects.filter(status=False).count()
        else:
            avatar_status['block'] = AddAccount.objects.filter(status=False, created_by= user.username).count()
        
        avatar_status_array = [{"Category":"block",
                                "value":avatar_status['block']},
                                {"Category":"engaged",
                                "value":avatar_status['engaged']},
                                {"Category":"free",
                                "value":avatar_status['free']},]

        response = {
            'action_stats': action_stats,
            'avatar_social_media_stats': final,
            'avatar_types': avatar_types_list,
            'total_avatars': total_avatars,
            'total_fake_ids': total_fake_ids,
            'avatar_status':avatar_status_array,
            'upcomming_task':all_data
        }
        return Response(response)
    

    def social_acc_relogin(self, request):
        # auth_user = request.user.has_perm("avatar_management.amu_permission")

        # if auth_user == False:
        #     response = {
        #         'message': 'permission missing',
        #         'status': False,
        #         'result': None
        #         }
        
        #     return Response(response,status=status.HTTP_403_FORBIDDEN)        

        if not request.data:
            response = {
                'message': 'Empty Request Data'
            }

            return Response(response)
            
        try:
            serializer = SocialReloginSerializer(data=request.data)

            if serializer.is_valid():
                response = ess_obj.social_acc_login(id=serializer.data['id'], email=serializer.data['email'], 
                username=serializer.data['username'], social_media=serializer.data['social_media'], status=serializer.data['status'])
                response = {
                    'message': response
                }
            else:
                response = {
                    'message': serializer.errors
                }
        except Exception as e:
            response = {
                'message': str(e)
            }

        return Response(response)
            