# from ocs_rest.keybase_management.views import KeybaseReport

from os import EX_CANTCREAT
from django.core.paginator import Paginator
import requests
import datetime
from itertools import chain
from typing_extensions import Final

import requests
from core_management import serializers
from rest_framework.views import exception_handler
# from ocs_rest.avatar_management import serializers
from portfolio_management.serializers import EventSerializer, GroupSerializer, IndividualSerializer, portfolioserializer
from case_management.models import Case
from django.db import (IntegrityError,
                       InternalError)
                       
from OCS_Rest.settings import HDFS_ROOT_PATH
from core_management.models import Log
from core_management.serializers import LogSerializersversion2
from report_management.serializers import NotesSerializer
from rest_framework.renderers import JSONRenderer
from core_management.hdfs_client import delete_file_hdfs
from rest_framework import authentication, pagination
from rest_framework import viewsets, status, mixins
from rest_framework.decorators import action
from rest_framework.decorators import permission_classes
from case_management.serializers import CaseDashboardsSerializer
from keybase_management.serializers import KeybaseSerializer
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from portfolio_management.models import Event, Group, Individual, Portfolio
from rest_framework.response import Response
from target_management.data_cleaning import ElasticSearchResponseClean
from core_management import elasticsearch_handler_v2
from keybase_management.models import Keybase
from target_management import ess_controller
from target_management.bds_controller import BDSController
from target_management.constants import TARGET_INDEX_RESOLVE, INDEX_LIST, KEYBASE_INDEX_LIST, GENERIC_INDEX_LIST, \
    INDEX_PLATFORM_ALL
from target_management.models import SocialTarget, KeybaseTarget, GenericTarget, Target, UserNews
from target_management.signals import get_attribute
from target_management.clean_data import clean_response
from .serializers import (
    SocialTargetListSerializer,
    GenericTargetListSerializer,
    KeybaseTargetListSerializer,
    KeybaseTargetListSerializerV2,
    ReportsNotesSerialized,
    SocialTargetListSerializerV1,
    SocialTargetListSerializerV2,
    GenericTargetListSerializerV1,
    GenericTargetListSerializerV2,
    UserNewsSerializer,
    TargetShareResourceSerializer,
    GTRArchiveTargetSerializer,
    TargetLinkAnalysisResponseSerializer, SocialMediaAccountSettings)
from core_management.publisher import Rabbit_Publisher
from target_management.constants import SERVER_CODE, NEW_SERVER_CODE, target_status_dic, auto_update_status_dic
from account_management.models import User
from target_management.sds_controller import SDSController
from report_management.models import ReportsNotes
from target_management.custom_permission import UserObjectAcessPermission
import json
import re
from core_management.sftp_upload import FTP_Client
from django.utils import timezone
from django.db.models import Q
import math
from django.forms.models import model_to_dict
from .target_identify_socket import TargetIdentifySocialMedia
from target_management.periodic_calls import PeriodicCall


# from datetime import datetime
# from categorization_visualization import get_categorization_visual


es_clean = ElasticSearchResponseClean()
es_object = elasticsearch_handler_v2.ElasticsearchHandler()
ess_object = ess_controller.EssApiController()
bds_object = BDSController()
sds_object = SDSController()
publisher_obj = Rabbit_Publisher()
# target_status_dic ={"0":"1","12":"2","24":"2","23":"3","26":"3","13":"3","32":"4","28":"5","30":"5","44":"6","62":"7"}

def get_index_to_delete_doc(gtr):
    platform_type = gtr.split('_')[1]
    translated_dict = dict(INDEX_PLATFORM_ALL)
    print("translated_dict", translated_dict)
    translated_string = translated_dict[str(platform_type)]
    print(translated_string)
    return translated_string

def get_index_for_es(target_type, target_sub_type, index):
    to_translate = str(target_type) + ',' + str(target_sub_type)
    translate_target = dict(TARGET_INDEX_RESOLVE)
    index_translated = translate_target[str(to_translate)]
    return_index = index_translated + index
    return return_index


def translate_status_from_status_code(status_code):
    translated_dict = dict(SERVER_CODE)
    print("translated_dict", translated_dict)
    translated_string = translated_dict[str(status_code)]
    print(translated_string)
    return translated_string

def translate_status_from_json_status_code(status_code):
    translated_dict = dict(NEW_SERVER_CODE)
    print("translated_dict", translated_dict)
    translated_string = translated_dict[str(status_code)]
    print(translated_string)
    return translated_string


class TargetSearch(viewsets.ViewSet):
    """
    Viewset for smart search and query search
    """
    authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (DjangoModelPermissions, IsAuthenticated,)

    @action(detail=True, methods=['GET'])
    def get_status(self, request):
        user = request.user
        print("Request By User", user)
        if 'GTR' in request.query_params:
            GTR = request.query_params['GTR']
            print(GTR)
        else:
            GTR = None
        if GTR:
            target_type = GTR.split('_')[0]
            try:
                if target_type == 'st':
                    target_object = SocialTarget.objects.get(GTR=GTR)
                    target_status = target_object.target_status
                elif target_type == 'dt':
                    target_object = GenericTarget.objects.get(GTR=GTR)
                    target_status = target_object.target_status
                elif target_type == 'kb':
                    target_object = KeybaseTarget.objects.get(GTR=GTR)
                    target_status = target_object.target_status
                else:
                    target_status = None
                if target_status is None:
                    response = {'message': 'GTR not found',
                                'status': True,
                                'result': target_status}
                    publisher_obj.publish(response)
                    return Response(response, status=status.HTTP_200_OK)

                response = {'message': 'Target Status',
                            'status': True,
                            'result': target_status}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_200_OK)
            except Exception as E:
                # print(E)
                response = {'message': 'Error while Searching GTR ',
                            'status': True,
                            'result': None}
                return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'message': 'GTR not given in params',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def update_status(self, request):
        user = request.user
        print("Request By User", user)
        print("Request for update")
        print("---------", request.data)
        if 'GTR' in request.data:
            GTR = request.data['GTR']
            print(GTR)
        else:
            GTR = None

        if 'target_status' in request.data:
            target_status = request.data['target_status']
            print(target_status)
        else:
            target_status = None

        time = timezone.now()
        time = time.strftime("%x %X") 

        time1 = datetime.datetime.now()
        time1 = time1.strftime("%x %X") 
        # time = timezone.localtime(timezone.now()).strftime("%x %X")
        print("------------------datetime -------------------------", time1)
        print("------------------django -------------------------", time)


        # target_status_dic ={"0":"1","12":"2","24":"2","23":"3","26":"3","13":"3","32":"4","28":"5","30":"5","44":"6","62":"7"}
        # print(check["3"])
        if target_status in target_status_dic:
            print("yes")
            # translate_status_from_json_status_code
        else:
            print("no")
        
        if all(v is not None for v in [GTR, target_status]):
            """ 
            reason for writing all this code is because sometime the flow ot status get broken. 
            for example: if crowling fail message are send by ess and the target is already crawled by recraling 
            
            """
            target_type = GTR.split('_')[0]
            try:
                if target_type == 'st':
                    target_object = SocialTarget.objects.get(GTR=GTR)
                    translated_status = translate_status_from_status_code(status_code=target_status)
                    status_string = target_object.target_status_string + ',' + translated_status + "," + str(time)
                    updated = SocialTarget.update_status(target_object, target_status, status_string)
                    dic_ = target_object.target_status_dic
                    if str(target_status) in target_status_dic:
                        if str(target_status) == "24":
                            for key , value in dic_.items():
                                if value['message'] != 'Target Marked':
                                    value['time'] = ""
                        if str(target_status) == "32" or str(target_status) == "30" or str(target_status) == "28" :
                            if "3" in dic_:
                                if dic_["3"]['message'] == "Crawling Failed":
                                    dic_["3"]['message'] = "Crawling Completed"
                        new_auto_update_status_dic = {value:key for key, value in auto_update_status_dic.items()}

                        dic_[target_status_dic[str(target_status)]] =  {"message": translate_status_from_json_status_code(status_code=target_status), "time":str(time), "server_request":True  } 
                        for each_key in range(int(target_status_dic[str(target_status)]),0,-1):
                            if str(each_key) not in dic_:
                                dumping_target_status =new_auto_update_status_dic[str(each_key)]
                                dic_[target_status_dic[str(dumping_target_status)]] =  {"message": translate_status_from_json_status_code(status_code=dumping_target_status), "time":str(time) ,"server_request":False  } 
                                

                                

                        target_object.update()

                    else:
                        print("no")
                elif target_type == 'dt':
                    target_object = GenericTarget.objects.get(GTR=GTR)
                    translated_status = translate_status_from_status_code(status_code=target_status)
                    status_string = target_object.target_status_string + ',' + translated_status + "," + str(time)
                    updated = GenericTarget.update_status(target_object, target_status, status_string)
                    dic_ = target_object.target_status_dic
                    if str(target_status) in target_status_dic:
                        if str(target_status) == "24":
                            for key , value in dic_.items():
                                if value['message'] != 'Target Marked':
                                    value['time'] = ""
                        if str(target_status) == "32" or str(target_status) == "30" or str(target_status) == "28" :
                            if "3" in dic_:
                                if dic_["3"]['message'] == "Crawling Failed":
                                    dic_["3"]['message'] = "Crawling Completed"
                        new_auto_update_status_dic = {value:key for key, value in auto_update_status_dic.items()}

                        dic_[target_status_dic[str(target_status)]] =  {"message": translate_status_from_json_status_code(status_code=target_status), "time":str(time), "server_request":True  } 
                        for each_key in range(int(target_status_dic[str(target_status)]),0,-1):
                            if str(each_key) not in dic_:
                                dumping_target_status =new_auto_update_status_dic[str(each_key)]
                                dic_[target_status_dic[str(dumping_target_status)]] =  {"message": translate_status_from_json_status_code(status_code=dumping_target_status), "time":str(time) ,"server_request":False  } 
                                




                        target_object.update()
                elif target_type == 'kb':
                    target_object = KeybaseTarget.objects.get(GTR=GTR)
                    translated_status = translate_status_from_status_code(status_code=target_status)
                    status_string = target_object.target_status_string + ',' + translated_status + "," + str(time)
                    updated = KeybaseTarget.update_status(target_object, target_status, status_string)
                    dic_ = target_object.target_status_dic
                    if str(target_status) in target_status_dic:
                        if str(target_status) == "24":
                            for key , value in dic_.items():
                                if value['message'] != 'Target Marked':
                                    value['time'] = ""
                        if str(target_status) == "32" or str(target_status) == "30" or str(target_status) == "28" :
                            if "3" in dic_:
                                if dic_["3"]['message'] == "Crawling Failed":
                                    dic_["3"]['message'] = "Crawling Completed"
                        new_auto_update_status_dic = {value:key for key, value in auto_update_status_dic.items()}

                        dic_[target_status_dic[str(target_status)]] =  {"message": translate_status_from_json_status_code(status_code=target_status), "time":str(time), "server_request":True } 
                        
                        for each_key in range(int(target_status_dic[str(target_status)]),0,-1):
                            if str(each_key) not in dic_:
                                dumping_target_status =new_auto_update_status_dic[str(each_key)]
                                dic_[target_status_dic[str(dumping_target_status)]] =  {"message": translate_status_from_json_status_code(status_code=dumping_target_status), "time":str(time) ,"server_request":False  } 
                                

                        
                        
                        target_object.update()
                else:
                    updated = False
                if not updated:
                    response = {'message': 'Updating Failed',
                                'status': updated,
                                'result': target_status}
                    publisher_obj.publish(response)
                    return Response(response, status=status.HTTP_409_CONFLICT)

                response = {'message': 'Status Updated',
                            'status': updated,
                            'result': target_status}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_200_OK)
            except Exception as E:
                # print(E)
                response = {'message': 'GTR not found',
                            'status': False,
                            'result': None}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'message': 'GTR or target_status not given in params',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def query(self, request):
        auth_user = request.user.has_perm("target_management.can_mark_targets")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        user = request.user
        print('HERE')
        user = request.user
        print("Request By User", user)
        print(request.data)
        if 'search_query' in request.data:
            search_query = request.data['search_query']
            print(search_query)
        else:
            search_query = None
        if 'target_type' in request.data:
            target_type = request.data['target_type']

        else:
            target_type = None
        if target_type == 'in':
            social_type = 'instagram'
        elif target_type == 'fb':
            social_type = 'facebook'
        elif target_type == 'tw':
            social_type = 'twitter'
        elif target_type == 'rd':
            social_type = 'reddit'
        elif target_type == 'ln':
            social_type = 'linkedin'
        elif target_type == 'tk':
            social_type = 'tiktok'
        elif target_type == 'tb':
            social_type = 'tumblr'
        else:
            print("in else")
            social_type = ''
        try:

            social_media_accounts = ess_object.getall_sm_account()
            print("social_media_accounts",social_media_accounts)
            for data in social_media_accounts['accounts']:
                if social_type == data['social_media']:
                    if data['status'] != 1:
                        response = {
                            'message': "{social_media} Avatar is Blocked".format(social_media=social_type)
                        }
                        return Response(response)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        if all(v is not None for v in [search_query, target_type]):
            try:
                if target_type == 'in':
                    # import threading
                    # threading.Thread(ge)
                    result = TargetIdentifySocialMedia().start_targetidentify(target="instagram",query=str(search_query))
                    # result = ess_object.instagram_target_identification(query=str(search_query))
                elif target_type == 'fb':
                    result = TargetIdentifySocialMedia().start_targetidentify(target="facebook",query=str(search_query))
                    # result = ess_object.facebook_target_identification(query=str(search_query))
                elif target_type == 'tw':
                    result = TargetIdentifySocialMedia().start_targetidentify(target="twitter",query=str(search_query))
                    # result = ess_object.twitter_target_identification(query=str(search_query))
                elif target_type == 'yt':
                    result = TargetIdentifySocialMedia().start_targetidentify(target="youtube",query=str(search_query))
                    # result = ess_object.youtube_target_identification(query=str(search_query))
                elif target_type == 'ln':
                    result = TargetIdentifySocialMedia().start_targetidentify(target="linkedin",query=str(search_query))
                    # result = ess_object.linkedin_target_identification(query=str(search_query))
                elif target_type == 'rd':
                    result = TargetIdentifySocialMedia().start_targetidentify(target="reddit",query=str(search_query))
                    # result = ess_object.reddit_target_identification(query=str(search_query))
                elif target_type == 'tk':
                    result = TargetIdentifySocialMedia().start_targetidentify(target="tiktok",query=str(search_query))
                    # result = ess_object.tiktok_target_identification(query=str(search_query))
                elif target_type == 'tb':
                    result = TargetIdentifySocialMedia().start_targetidentify(target="tumblr",query=str(search_query))
                    # result = ess_object.tumblr_target_identification(query=str(search_query))
                else:
                    result = None
                print(result)
                response = {'message': 'Search result',
                            'status': True,
                            'result': result}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_200_OK)
            except InternalError:
                response = {'message': 'Error while calling crawler api',
                            'status': True,
                            'result': None}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'message': 'Search query or target type missing',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def smart(self, request):
        auth_user = request.user.has_perm("target_management.can_mark_targets")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        user = request.user
        print('data', request.data)
        print("Request By User", user)
        print("------------------------", request.data)
        if 'username' in request.data:
            username = request.data['username']
        else:
            username = None
        if 'target_type' in request.data:
            target_type = request.data['target_type']
        else:
            target_type = None
        if 'target_sub_type' in request.data:
            target_sub_type = request.data['target_sub_type']
        else:
            target_sub_type = None

        if target_type == 'in':
            social_type = 'instagram'
        elif target_type == 'fb':
            social_type = 'facebook'
        elif target_type == 'tw':
            social_type = 'twitter'
        elif target_type == 'rd':
            social_type = 'reddit'
        elif target_type == 'ln':
            social_type = 'linkedin'
        elif target_type == 'tk':
            social_type = 'tiktok'
        elif target_type == 'sc':
            social_type = 'snapchat'
        else:
            social_type = ''
        try:
            if social_type != "snapchat":
                social_media_accounts = ess_object.getall_sm_account()
                print("social_media_accounts----------------->",social_media_accounts)
                for data in social_media_accounts['accounts']:
                    if social_type == data['social_media']:
                        if data['status'] != 1:
                            response = {
                                'message': "{social_media} Avatar is Blocked".format(social_media=social_type)
                            }
                            return Response(response)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        if all(v is not None for v in [username, target_type, target_sub_type]):
            try:
                target_type, target_sub_type = get_attribute(target_type=target_type, sub_target_type=target_sub_type)
                result = ess_object.ess_add_smart_search_target(username=username, target_type=target_type,
                                                                subtype=target_sub_type)
                print('result', result)
                response = {'message': 'Result',
                            'status': True,
                            'result': result}
                print('response', response)
                return Response(response, status=status.HTTP_200_OK)
            except InternalError:
                response = {'message': 'Error while calling crawler api',
                            'status': True,
                            'result': None}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'message': 'username or target type missing',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def survey(self, request):
        auth_user = request.user.has_perm("target_management.can_create_internet_survey")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        user = request.user
        print("Request By User", user)
        print('payload', request.data)
        if 'name' in request.data:
            name = request.data['name']
        else:
            name = None
        if 'email' in request.data:
            email = request.data['email']
        else:
            email = None
        if 'phone' in request.data:
            phone = request.data['phone']
        else:
            phone = None
        if 'address' in request.data:
            address = request.data['address']
        else:
            address = None
        if any(v is not None for v in [name, email, phone, address]):
            try:
                result = ess_object.target_internet_survey(name=name, email=email, phone=phone, address=address)
                response = {'status': True,
                            'result': result}
                print('response', response)
                # publisher_obj.publish(response)
                return Response(response, status=status.HTTP_200_OK)
            except InternalError:
                response = {'message': 'Error while calling crawler api',
                            'status': True,
                            'result': None}
                return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'message': 'username or target type missing',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def fetch_again(self, request):
        if all(v is not None for v in [request.data['GTR']]):
            gtr = request.data['GTR']
            
            print("-------------------", gtr)
            try:
                target_type = gtr.split('_')[0]
                print('social_media_type', target_type)
                if target_type == 'st':
                    if SocialTarget.objects.filter(GTR=gtr):
                        target = SocialTarget.objects.filter(GTR=gtr).first()
                        target.update_ctr(obj=target, ctr=target.CTR, new_revoke=target.revoked_on)
                        target = SocialTarget.objects.filter(GTR=gtr).first()
                        target_type, target_sub_type, username, max_posts = \
                            target.target_type, target.target_sub_type, target.user_names, target.max_posts
                    else:
                        target = None
                        target_type, target_sub_type, username, max_posts = None, None, None, None
                elif target_type == 'dt':
                    try:
                        vpn = request.data['vpn']

                    except:
                        vpn = False
                    if GenericTarget.objects.filter(GTR=gtr):
                        target = GenericTarget.objects.filter(GTR=gtr).first()
                        # target_type, target_sub_type, username = \
                        #     target.target_type, target.target_sub_type, target.url
                        resp = ess_object.dynamic_crawling(url=target.url, ip_address=target.ip, domain=target.domain,
                                                           pictures=target.pictures, videos=target.videos,
                                                           heading=target.headings, paragraphs=target.paragraphs,
                                                           links=target.links, GTR=target.GTR, CTR=target.CTR, vpn=vpn)
                        response = {
                            'message': 'successfull',
                            'result': resp
                        }
                        return Response(response)
                    else:
                        target = None
                        target_type, target_sub_type, username = None, None, None
                else:
                    target = None
                    target_type, target_sub_type, username = None, None, None
                if target is None:
                    response = {
                        'message':
                            'Target object not found for selected GTR',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                if all(v is not None for v in [username, target_type, target_sub_type]):
                    if ess_object.connect():
                        target_type, sub_type = get_attribute(target_type=target.target_type,
                                                              sub_target_type=target.target_sub_type)
                        resp = ess_object.add_target(username=target.user_names, target_type=target_type,
                                                     target_sub_type=sub_type, GTR=target.GTR,
                                                     CTR=target.CTR, max_posts=target.max_posts)
                    else:
                        resp = 'Micro crawler connection error'
                else:
                    resp = None
                response = {
                    'message': 'Target fetch request Successfully',
                    'status': True,
                    'result': resp
                }
                return Response(response,
                                status=status.HTTP_200_OK)

            except Exception as e:
                import traceback
                traceback.print_exc()
                response = {
                    'message': str(e),
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'data missing',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)
    @action(detail=True, methods=['GET'])
    def periodicCallTest(self, request):
        try:
            calls = PeriodicCall()
            calls.add_target()
            return Response("yes its start working ")
        except:
            return Response("NO its not start working ")


class SocialTargetView(viewsets.ViewSet):
    """
    Viewset for Social target add, delete, update and list
    """
    authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (IsAuthenticated,DjangoModelPermissions)
    #queryset = SocialTarget.objects.all().order_by('-created_on')

    def get_serializer_class(self):
        #print(self.request.version)
        if self.request.version == 'v1':
            return SocialTargetListSerializer
        return SocialTargetListSerializer

    @action(detail=True, methods=['GET'])
    def list(self, request):
        user = request.user
        all_users = User.objects.with_perm('target_management.view_socialtarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to access scoial target',
                'status': False,
                'result': None
            }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
       
    
        # if not request.user in all_users:
        #     response = {
        #         'message': 'User has no permission to view Social Targets'
        #     }
        #     print(response)
        #     return Response(response)
        if 'target_id' in request.data:
            target_id = str(request.data['target_id'])
            targets = SocialTarget.objects.filter(id=target_id)
        else:
            user_obj = User.objects.get(username=request.user)
            print('------------', user_obj.id)
            # targets = SocialTarget.objects.filter(user_id=user_obj.id)
            if user.is_superuser:
                targets = SocialTarget.objects.all()
                # paginator = Paginator(targets, 500)
                # pages_number = paginator.num_pages
                # targets = paginator.page(pages_number)
            else:
                targets = SocialTarget.objects.filter( user = user)

        if targets:
            result = self.get_serializer_class()(
                instance=targets,
                many=True).data
            for r in result:
                obj = User.objects.get(id=r['user'])
                r['user'] = obj.username
            response = {'message': 'List all the Targets',
                        'status': True,
                        'result': result}
            return Response(response,
                            status=status.HTTP_200_OK)
        else:
            response = {
                'message': 'No Target Found',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['GET'])
    def listV1(self, request):
        user = request.user
        all_users = User.objects.with_perm('target_management.view_socialtarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to access scoial target',
                'status': False,
                'result': None
            }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        check = 0
        target_type = self.request.query_params.get('target_type')
        page = self.request.query_params.get('page')
        user_name = self.request.query_params.get('user_name')
        status_ = self.request.query_params.get('status')
        # NEW_SERVER_CODE
        if status_:
            #(target_status_dic__1__message__icontains= "Target")
            server_code = dict(NEW_SERVER_CODE)
            for key, values in server_code.items():
                if values.find(status_) != -1:
                    print("founds!")
                    query_number = target_status_dic[str(key)]

            qrt = {"target_status_dic__{0}__message__icontains".format(query_number):status_}
            # for i in range(1,5):
            query = Q(**qrt)
            print(query)
            check = 1
            
       
        if target_type:
            if check==0:
                query = Q(target_type=target_type)
                check = 1
            else:
                query.add(Q(target_type=target_type), Q.AND)


        if user_name:
            if check == 0:
                query = Q(user_names__icontains=user_name)
                check = 1
            else:
                query.add(Q(user_names__icontains=user_name), Q.AND)
        
                
        if user.is_superuser:
            try:
                
                targets = SocialTarget.objects.filter(query).order_by('-created_on')
                targets_count = SocialTarget.objects.filter(query).count()
            except:
                targets = SocialTarget.objects.all().order_by('-created_on')
                targets_count = SocialTarget.objects.all().count()
        else:
            if check == 0:
                query = Q(user=user)
                check = 1
            else:
                query.add(Q(user=user), Q.AND)


            query.add(Q(share_resource__contains=[user.id]), Q.OR)
            targets = SocialTarget.objects.filter(query).order_by('-created_on')
            targets_count = SocialTarget.objects.filter(query).count()

        paginator = Paginator(targets, 8)
        targets = paginator.page(int(page))
        # if 'target_id' in request.data:
        #     target_id = str(request.data['target_id'])
        #     targets = SocialTarget.objects.filter(id=target_id)
        #     check = 1 
        # else:


        #     if user.is_superuser:
        #         targets = SocialTarget.objects.all()
        #         targets_count = SocialTarget.objects.count()
        #         print({'targets_count':targets_count})
        #         paginator = Paginator(targets, 4)
        #         pages_number = paginator.num_pages
        #         targets = paginator.page(2)
        #     else:
        #         targets = SocialTarget.objects.filter( user = user)

        if targets:
            result = SocialTargetListSerializerV1(targets, many = True)
            response = {'message': 'List all the Targets',
                        'status': True,
                        'targets_count':targets_count,
                        "pages": math.ceil(targets_count/8),
                        "current_page":int(page),
                        'result': result.data,
                        }
            return Response(response,
                            status=status.HTTP_200_OK)
        else:
            response = {
                'message': 'No Target Found',
                'status': False,
                'result': None
            }
            # publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['GET'])
    def listV2(self, request):
        user = request.user
        print("user.username",user.username)
        all_users = User.objects.with_perm('target_management.view_socialtarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to access scoial target',
                'status': False,
                'result': None
            }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        check = 0
        search = self.request.query_params.get('search')
        page = self.request.query_params.get('page')
        

        if search:
            social_query = Q()
            generic_query = Q()
            keybase_query = Q()

            
                


                

            if check == 0:
                social_query = Q(GTR__icontains = search)
                generic_query = Q(GTR__icontains = search)
                keybase_query = Q(GTR__icontains = search)
                check = 1
            else:
                social_query.add(Q(GTR__icontains = search), Q.AND)
                generic_query.add(Q(GTR__icontains = search), Q.AND)
                keybase_query.add(Q(GTR__icontains = search), Q.AND)



            social_query.add(Q(user_names__icontains=search), Q.OR)
            social_query.add(Q(full_name__icontains=search), Q.OR)

            generic_query.add(Q(title__icontains=search), Q.OR)

            keybase_query.add(Q(keybase_title__icontains=search), Q.OR)


            if user.is_superuser == False:
                if check == 0:
                    social_query = Q(user = user)
                    generic_query = Q(user = user)
                    keybase_query = Q(user = user)

                    social_query.add(Q(share_resource__contains=[user.id]), Q.OR)
                    generic_query.add(Q(share_resource__contains=[user.id]), Q.OR)
                    keybase_query.add(Q(share_resource__contains=[user.id]), Q.OR)
                    check = 1
                else:
                    social_query.add(Q(user = user), Q.AND)
                    generic_query.add(Q(user = user), Q.AND)
                    keybase_query.add(Q(user = user), Q.AND)

                    social_query.add(Q(share_resource__contains=[user.id]), Q.OR)
                    generic_query.add(Q(share_resource__contains=[user.id]), Q.OR)
                    keybase_query.add(Q(share_resource__contains=[user.id]), Q.OR)
                    

            social = SocialTarget.objects.filter(social_query).order_by('-created_on')
            generic = GenericTarget.objects.filter(generic_query).order_by('-created_on')
            keybase = KeybaseTarget.objects.filter(keybase_query).order_by('-created_on')

            targets_count = SocialTarget.objects.filter(social_query).count() + GenericTarget.objects.filter(generic_query).count() + KeybaseTarget.objects.filter(keybase_query).count()

        else:
            if request.user.is_superuser:
                social = SocialTarget.objects.all().order_by('-created_on')
                generic = GenericTarget.objects.all().order_by('-created_on')
                keybase = KeybaseTarget.objects.all().order_by('-created_on')
            else:
                if check == 0:
                    social_query = Q(user = user)
                    generic_query = Q(user = user)
                    keybase_query = Q(user = user)
                    check = 1
                
                social_query.add(Q(share_resource__contains=[user.id]), Q.OR)
                generic_query.add(Q(share_resource__contains=[user.id]), Q.OR)
                keybase_query.add(Q(share_resource__contains=[user.id]), Q.OR)

                social = SocialTarget.objects.filter(social_query).order_by('-created_on')
                generic = GenericTarget.objects.filter(generic_query).order_by('-created_on')
                keybase = KeybaseTarget.objects.filter(keybase_query).order_by('-created_on')


            if user.is_superuser:
                targets_count = SocialTarget.objects.all().count() + GenericTarget.objects.all().count() + KeybaseTarget.objects.all().count()
            else:
                targets_count = SocialTarget.objects.filter(social_query).count() + GenericTarget.objects.filter(generic_query).count() + KeybaseTarget.objects.filter(keybase_query).count()

        orders = list(
            sorted(
                chain(social, generic, keybase ),
                key=lambda objects: objects.created_on,
                reverse=True
            ))

        paginator = Paginator(orders, 8)
        targets = paginator.page(int(page))
        
        if targets:
            result = []
            # result = GTRArchiveTargetSerializer(targets, many=True)
            # result = [model_to_dict(each_target) for each_target in targets.object_list]
            for each_target in targets.object_list:
                
                if isinstance(each_target, SocialTarget):
                    # print("sssssssssssssssssssssss")
                    result.append(SocialTargetListSerializerV2(each_target).data)
                elif isinstance(each_target, KeybaseTarget):
                    # print("kkkkkkkkkkkkkkkkkkkk")
                    result.append(KeybaseTargetListSerializerV2(each_target).data)
                elif isinstance(each_target, GenericTarget):
                    # print("gggggggggggggggggggggg")
                    result.append(GenericTargetListSerializerV2(each_target).data)
            # result = model_to_dict(targets.object_list)
            response = {'message': 'List all the Targets',
                        'status': True,
                        'targets_count':targets_count,
                        "pages": math.ceil(targets_count/8),
                        "current_page":int(page),
                        'result': result,
                        }
            return Response(response,
                            status=status.HTTP_200_OK)
        else:
            response = {
                'message': 'No Target Found',
                'status': False,
                'result': None
            }
            # publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True,
            methods=['POST'])
    def create(self, request):

        all_users = User.objects.with_perm('target_management.add_socialtarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to Create Social Targets'
            }
            return Response(response)
        var = True
        target_detail = request.data.copy()

        expire_date = datetime.datetime.fromtimestamp(
            float(target_detail['expire_on']) / 1000) + datetime.timedelta(hours=11)
        target_detail.update({'expire_on': expire_date})
        username = request.data['user_names']
        target_type = request.data['target_type']
        target_sub_type = request.data['target_sub_type']

        user_chech = SocialTarget.objects.filter(user_names= username, target_type=target_type )
        if user_chech:
            response = {
                    'message': "Target user_name '{0}' already marked".format(username),
                    'status': True,
                    'result': []
                }
            return Response(response,
                            status=status.HTTP_200_OK)

        avatar_password = request.data['avatar_password']
        avatar_username = request.data['avatar_username']

        social_media_accounts = ess_object.getall_sm_account()
        if target_type == 'in':
            social_type = 'instagram'
        elif target_type == 'fb':
            social_type = 'facebook'
        elif target_type == 'tw':
            social_type = 'twitter'
        elif target_type == 'rd':
            social_type = 'reddit'
        elif target_type == 'ln':
            social_type = 'linkedin'
        elif target_type == 'tk':
            social_type = 'tiktok'
        elif target_type == 'sc':
            social_type = 'snapchat'
        elif target_type == 'tb':
            social_type = 'tumblr'
        else:
            print("in else")
            social_type = ''
        for data in social_media_accounts['accounts']:
            if social_type == data['social_media']:
                if data['status'] != 1:
                    response = {
                        'message': "{social_media} Avatar is Blocked".format(social_media=social_type)
                    }
                    print(response)
                    return Response(response)
        social_target_obj = SocialTarget.objects.all()
        for obj in social_target_obj:
            if username.lower() == obj.user_names.lower() and target_type == obj.target_type and target_sub_type == obj.target_sub_type:
                var = False
        if var == False:
            response = {
                'message': 'Username Already Marked'
            }
            return Response(response)

        if not SocialTarget.get_social_target_count():
            response = {
                'message': 'Targets Limit Exceeded For Today'
            }
            return Response(response)
        if request.data is not None:
            try:
                target = SocialTarget()
                for attr, value in target_detail.items():
                    setattr(target, attr, value)
                    print('Attribute', attr)
                    print('Value', value)

                created = target.save()

                if created:
                    result = self.get_serializer_class()(
                        instance=target,
                        many=False).data
                else:
                    result = "Target not Marked"
                

                # result['amu']={
                #     'avatar_username':avatar_username,
                #     'avatar_password':avatar_password

                # }
                print('----------------------------------------')
                result['avatar_username']=avatar_username
                result['avatar_password']=avatar_password
            
                print('result--------:',result)
                response = {
                    'message': 'Target Created Successfully',
                    'status': True,
                    'result': result
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_200_OK)
            except Exception as e:
                response = {
                    'message': 'Target url Already found  {0}'.format(e) ,
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_204_NO_CONTENT)

            except Exception as E:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': str(E)
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

        else:
            response = {
                'message': 'Please provide the data',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True,
            methods=['POST'])
    def create_bulk_target(self, request):
        auth_user = request.user.has_perm("target_management.can_mark_targets")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        target_detail = request.data.copy()
        print(target_detail)
        bulk_keys = {*target_detail}
        print(target_detail)
        if bulk_keys == {'expire_on', 'target_type', 'target_sub_type', 'usernames', 'max_post'}:
            print(bulk_keys)
            expire_date = datetime.datetime.fromtimestamp(
                float(target_detail['expire_on']) / 1000) + datetime.timedelta(hours=11)
            target_detail.update({'expire_on': expire_date})
            bulk_target_username = target_detail['usernames']
            target_type = target_detail['target_type']
            print(target_type)
            target_sub_type = target_detail['target_sub_type']
            max_posts = target_detail['max_post']
            expiry = target_detail['expire_on']
            if target_type == 'gn':
                for urls in bulk_target_username:
                    try:
                        target = GenericTarget(title=urls, url=urls,
                                               headings=True, paragraphs=True, target_type=target_type,
                                               target_sub_type=target_sub_type, expire_on=expire_date)
                        created = target.save()
                    except IntegrityError:
                        pass
                    except Exception as E:
                        pass

                    else:
                        pass
            else:
                for username in bulk_target_username:
                    target_type_t, target_sub_type_t = get_attribute(target_type=target_type,
                                                                     sub_target_type=target_sub_type)
                    response = ess_object.ess_add_smart_search_target(username=username, target_type=target_type_t,
                                                                      subtype=target_sub_type_t)
                    print(response)
                    if 'data' in response:
                        try:
                            smart_search_data = response['data']
                            print('data', smart_search_data)
                            if smart_search_data:
                                target = SocialTarget(userid=smart_search_data['id'], user_names=username,
                                                      full_name=smart_search_data['full_name'],
                                                      target_url=smart_search_data['profile_image_url'],
                                                      target_type=target_type, target_sub_type=target_sub_type,
                                                      max_posts=max_posts, expire_on=expiry)
                                created = target.save()
                                print(created)
                        except IntegrityError:
                            pass
                        except Exception as E:
                            pass

                    else:
                        pass
            response = {
                'message': 'Mark Completed',
                'status': False,
                'result': "Marked successfully"
            }
            return Response(response,
                            status=status.HTTP_200_OK)
        else:
            response = {
                'message': 'Data Missing',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['POST'])
    def update(self, request):
        all_users = User.objects.with_perm('target_management.change_socialtarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to Update Social Targets'
            }
            return Response(response)
        if 'target_id' in request.data:
            target_id = str(request.data['target_id'])
        else:
            target_id = None
        update_detail = request.data.copy()
        print(update_detail['expire_on'])
        print(update_detail['target_id'])
        if 'expire_on' in request.data:
            expire_date = datetime.datetime.fromtimestamp(
                float(update_detail['expire_on']) / 1000)
            update_detail.update({'expire_on': expire_date})
        if all(v is not None for v in [target_id, update_detail]):
            if SocialTarget.objects.filter(id=target_id):
                target = SocialTarget.objects.filter(id=target_id).first()
            else:
                target = None
                print('not')
            if target is None:
                response = {
                    'message': 'Target object not found for selected target',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_204_NO_CONTENT)
            try:
                for attr, value in update_detail.items():
                    setattr(target, attr, value)
                updated = target.update()
                if updated:
                    result = self.get_serializer_class()(
                        instance=target,
                        many=False).data
                else:
                    result = None
                response = {
                    'message': 'Target Updated Successfully',
                    'status': True,
                    'result': result
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Target url Already found',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params or data missing',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def destroy(self, request):
        all_users = User.objects.with_perm('target_management.delete_socialtarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to Delete Social Targets'
            }
            return Response(response)
        if 'target_id' in request.data:
            target_id = str(request.data['target_id'])
        else:
            target_id = None
        print('ressssssss', request.data)
        if all(v is not None for v in [target_id]):
            if SocialTarget.objects.filter(id=target_id):
                target = SocialTarget.objects.get(id=target_id)
                gtr = target.GTR
                es_object.delete_by_gtr(gtr)
                print('asdasdas', gtr)
            else:
                target = None
            if target is None:
                response = {
                    'message':
                        'Target object not found for selected target id',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_204_NO_CONTENT)

            try:
                print('heres')
                target.delete()
                ftp = FTP_Client()
                ftp.login()
                check = ftp.delete_dir_file(gtr)
                response = {
                    'message': 'Target Deleted Successfully',
                    'status': True,
                    'result': check
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_200_OK)

            except Exception as e:
                response = {
                    'message': str(e),
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params Missing',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)


class GenericTargetView(viewsets.ViewSet):

    """
    Viewset for Generic target add, delete, update and list
    """

    def get_queryset(self):
        return self.request.user.generictarget_set.all().order_by('-created_on')

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return GenericTargetListSerializer
        return GenericTargetListSerializer

    authentication_classes = (authentication.TokenAuthentication,)

    # permission_classes = (DjangoModelPermissions, IsAuthenticated,)
    # queryset = GenericTarget.objects.all().order_by('-created_on')

    #queryset = GenericTarget.objects.all().('order_by-created_on')

    @action(detail=True, methods=['GET'])
    def list(self, request):
        user = request.user
        all_users = User.objects.with_perm('target_management.view_generictarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to View Generic Targets'
            }
            return Response(response)
        if 'target_id' in request.query_params:
            target_id = str(request.query_params['target_id'])
            targets = GenericTarget.objects.filter(
                user=user,
                id=target_id)
        else:
            if user.is_superuser:
                targets = GenericTarget.objects.all()
            else: 
                targets = GenericTarget.objects.filter(user = user )
        if targets:
            result = self.get_serializer_class()(
                instance=targets,
                many=True).data
            for r in result:
                obj = User.objects.get(id=r['user'])
                r['user'] = obj.username
            response = {'message': 'List all the Targets',
                        'status': True,
                        'result': result}
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_200_OK)
        else:
            response = {
                'message': 'No Target Found',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['GET'])
    def listV1(self, request):
        user = request.user
        all_users = User.objects.with_perm('target_management.view_generictarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to View Generic Targets'
            }
            return Response(response)

        check = 0
        target_type = self.request.query_params.get('target_type')
        page = self.request.query_params.get('page')
        title = self.request.query_params.get('title')

        status_ = self.request.query_params.get('status')
        # NEW_SERVER_CODE
        if status_:
            #(target_status_dic__1__message__icontains= "Target")
            server_code = dict(NEW_SERVER_CODE)
            for key, values in server_code.items():
                if values.find(status_) != -1:
                    print("founds!")
                    query_number = target_status_dic[str(key)]

            qrt = {"target_status_dic__{0}__message__icontains".format(query_number):status_}
            # for i in range(1,5):
            query = Q(**qrt)

        if title:

            if check == 0:
                query = Q(title__icontains=title)
                check = 1
            else:
                query.add(Q(title__icontains=title), Q.AND)


  
        if user.is_superuser:
            try:
                targets = GenericTarget.objects.filter(query)
                targets_count = GenericTarget.objects.filter(query).count()
            except:
                targets = GenericTarget.objects.all()
                targets_count = GenericTarget.objects.all().count()
        else:
            if check == 0:
                query = Q(user=user)
                check = 1
            else:
                query.add(Q(user=user), Q.AND)
            
            query.add(Q(share_resource__contains=[user.id]), Q.OR)
            targets = GenericTarget.objects.filter(query)
            targets_count = GenericTarget.objects.filter(query).count()

        paginator = Paginator(targets, 8)
        targets = paginator.page(int(page))
        if targets:
            result = GenericTargetListSerializerV1(targets, many=True)
            
            response = {'message': 'List all the Targets',
                        'status': True,
                        'targets_count':targets_count,
                        "pages": math.ceil(targets_count/8),
                        "current_page":int(page),
                        'result': result.data,
                        }
            return Response(response,
                            status=status.HTTP_200_OK)
        else:
            response = {
                'message': 'No Target Found',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def create(self, request):
        all_users = User.objects.with_perm('target_management.add_generictarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to Create Generic Targets'
            }

            return Response(response)
        target_detail = request.data.copy()
        expire_date = datetime.datetime.fromtimestamp(
            float(target_detail['expire_on']) / 1000) + datetime.timedelta(hours=11)
        target_detail.update({'expire_on': expire_date})
        if not GenericTarget.get_generic_target_count():
            response = {
                'message': 'Generic Targets Limit Exceeded For Today'
            }
            return Response(response)
        if request.data is not None:
            try:
                target = GenericTarget()
                for attr, value in target_detail.items():
                    print(attr)
                    print(value)
                    setattr(target, attr, value)

                created = target.save()

                print(created)
                result = self.get_serializer_class()(instance=target,
                                                     many=False).data
                response = {
                    'message': 'Target Created Successfully',
                    'status': True,
                    'result': result
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_200_OK)
            except Exception as e:
                print("errors-->",e)
                response = {
                    'message': 'Target url Already found',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_200_OK)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_200_OK)

        else:
            response = {
                'message': 'Please provide the data',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def update(self, request):
        all_users = User.objects.with_perm('target_management.change_generictarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to Update Generic Targets'
            }
            return Response(response)
        if 'target_id' in request.query_params:
            target_id = str(request.query_params['target_id'])
        else:
            target_id = None
        update_detail = request.data.copy()
        if 'expire_on' in request.data:
            expire_date = datetime.datetime.fromtimestamp(
                float(update_detail['expire_on']))
            update_detail.update({'expire_on': expire_date})
        if all(v is not None for v in [target_id, update_detail]):
            if GenericTarget.objects.filter(id=target_id):
                target = GenericTarget.objects.filter(id=target_id).first()
            else:
                target = None
                print('not')
            if target is None:
                response = {
                    'message': 'Target object not found for selected target',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_204_NO_CONTENT)
            try:
                for attr, value in update_detail.items():
                    setattr(target, attr, value)
                target.update()
                response = {
                    'message': 'Target Updated Successfully',
                    'status': True,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Target url Already found',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params or data missing',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['GET'])
    def destroy(self, request):
        all_users = User.objects.with_perm('target_management.delete_generictarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to Delete Generic Targets'
            }
            return Response(response)
        if 'target_id' in request.data:
            target_id = str(request.data['target_id'])
        else:
            target_id = None
        print(target_id)
        if all(v is not None for v in [target_id]):
            if GenericTarget.objects.filter(id=target_id):
                target = GenericTarget.objects.filter(id=target_id).first()
                gtr = target.GTR
                es_object.delete_by_gtr(gtr)
            else:
                target = None
            if target is None:
                response = {
                    'message':
                        'Target object not found for selected target id',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_204_NO_CONTENT)

            try:
                target.delete()
                ftp = FTP_Client()
                ftp.login()
                check = ftp.delete_dir_file(gtr)
                response = {
                    'message': 'Target Deleted Successfully',
                    'status': True,
                    'result': check
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_200_OK)

            except Exception as e:
                response = {
                    'message': str(e),
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params Missing',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)


class KeybaseTargetView(viewsets.ViewSet):
    """
    Viewset for Generic target add, delete, update and list
    """

    authentication_classes = (authentication.TokenAuthentication,)
    # def get_queryset(self):
    #     return self.request.user.socialtarget_set.all().order_by('-created_on')

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return KeybaseTargetListSerializer
        return KeybaseTargetListSerializer

    @action(detail=True, methods=['GET'])
    def list(self, request):
        all_users = User.objects.with_perm('target_management.view_keybasetarget')
        if not request.user in all_users:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
    
        user = request.user
        user_obj = User.objects.get(username=user)
        if 'target_id' in request.query_params:
            target_id = str(request.query_params['target_id'])
            targets = KeybaseTarget.objects.filter(id=target_id)
        elif user_obj.is_superuser:
            # targets = KeybaseTarget.objects.filter(user_id=user_obj.id)
            targets = KeybaseTarget.objects.all()
        else:
            targets=KeybaseTarget.objects.filter(user_id=user_obj.id)    

        if targets:

            result = self.get_serializer_class()(
                instance=targets,
                many=True).data
            for r in result:
                obj = User.objects.get(id=r['user'])
                r['user'] = obj.username
            response = {'message': 'List all the Targets',
                        'status': True,
                        'result': result} 
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                'message': 'No Target Found',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['GET'])
    def listV1(self, request):
        all_users = User.objects.with_perm('target_management.view_keybasetarget')
        if not request.user in all_users:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        check = 0
        keybase_title = self.request.query_params.get('keybase_title')
        page = self.request.query_params.get('page')
        
        user = request.user
        user_obj = User.objects.get(username=user)
        if 'target_id' in request.query_params:
            target_id = str(request.query_params['target_id'])
            targets = KeybaseTarget.objects.filter(id=target_id)
        elif user_obj.is_superuser:
            # targets = KeybaseTarget.objects.filter(user_id=user_obj.id)
            if keybase_title:
                query = Q(keybase_title__icontains=keybase_title)
                targets = KeybaseTarget.objects.filter(query)
                targets_count = KeybaseTarget.objects.filter(query).count()
            else:
                targets = KeybaseTarget.objects.all()
                targets_count = KeybaseTarget.objects.all().count()

            
        else:
            if keybase_title:
                query = Q(keybase_title__icontains=keybase_title)
                query.add(Q(user_id=user_obj.id), Q.AND)
                query.add(Q(share_resource__contains=[user.id]), Q.OR)
                targets = KeybaseTarget.objects.filter(query)
                targets_count = KeybaseTarget.objects.filter(query).count()
            else:
                query = Q(user_id=user_obj.id)
                query.add(Q(share_resource__contains=[user.id]), Q.OR)
                targets=KeybaseTarget.objects.filter(query)
                
                targets_count = KeybaseTarget.objects.filter(query).count()   


        paginator = Paginator(targets, 9)
        targets = paginator.page(int(page))

        if targets:

            result = self.get_serializer_class()(
                instance=targets,
                many=True).data
            # for r in result:
            #     obj = User.objects.get(id=r['user'])
            #     r['user'] = obj.username
            response = {'message': 'List all the Targets',
                        'status': True,
                        'targets_count':targets_count,
                        "pages": math.ceil(targets_count/9),
                        "current_page":int(page),
                        'result': result}
            return Response(response, status=status.HTTP_200_OK)
        else:
            response = {
                'message': 'No Target Found',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def create(self, request):
        all_users = User.objects.with_perm('target_management.add_keybasetarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to Create Keybase Targets'
            }
            return Response(response)
        if not KeybaseTarget.get_keybase_target_count():
            response = {
                'message': 'Keybase Targets Limit Exceeded For Today'
            }
            return Response(response)
        if request.data:
            target_detail = request.data.copy()
            expire_date = datetime.datetime.fromtimestamp(
                float(target_detail['expire_on']) / 1000) + datetime.timedelta(hours=11)
            target_detail.update({'expire_on': expire_date})
            if 'keybase_id' in request.data:
                keybase_id = request.data['keybase_id']
                print(keybase_id)
                keybase_object = Keybase.objects.get(id=keybase_id)

                del target_detail['keybase_id']
            else:
                keybase_object = None
            target_detail.update({'keybase': keybase_object})

        else:
            target_detail = None
            keybase_object = None
        if all(v is not None for v in [target_detail, keybase_object]):
            try:
                target = KeybaseTarget()
                for attr, value in target_detail.items():
                    print(attr)
                    print(value)
                    setattr(target, attr, value)


                created = target.save()


                print(created)
                if created:
                    result = self.get_serializer_class()(instance=target,
                                                         many=False).data
                else:
                    result = None
                response = {
                    'message': 'Target Created Successfully',
                    'status': True,
                    'result': result
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Target url Already found',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

        else:
            response = {
                'message': 'Please provide the data',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def update(self, request):
        all_users = User.objects.with_perm('target_management.change_keybasetarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to Update Keybase Targets'
            }
            return Response(response)
        if 'target_id' in request.query_params:
            target_id = str(request.query_params['target_id'])
        else:
            target_id = None
        update_detail = request.data.copy()
        if 'expire_on' in request.data:
            expire_date = datetime.datetime.fromtimestamp(
                float(update_detail['expire_on']))
            update_detail.update({'expire_on': expire_date})
        if all(v is not None for v in [target_id, update_detail]):
            if KeybaseTarget.objects.filter(id=target_id):
                target = KeybaseTarget.objects.filter(id=target_id).first()
            else:
                target = None
                print('not')
            if target is None:
                response = {
                    'message': 'Target object not found for selected target',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_204_NO_CONTENT)
            try:
                for attr, value in update_detail.items():
                    setattr(target, attr, value)
                target.update()
                response = {
                    'message': 'Target Updated Successfully',
                    'status': True,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Target url Already found',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params or data missing',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['GET'])
    def destroy(self, request):
        all_users = User.objects.with_perm('target_management.delete_keybasetarget')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to Delete Keybase Targets'
            }
            return Response(response)
        if 'target_id' in request.data:
            target_id = str(request.data['target_id'])
        else:
            target_id = None
        print(target_id)
        if all(v is not None for v in [target_id]):
            if KeybaseTarget.objects.filter(id=target_id):
                target = KeybaseTarget.objects.filter(id=target_id).first()
                gtr = target.GTR
                es_object.delete_by_gtr(gtr)
            else:
                target = None
            if target is None:
                response = {
                    'message':
                        'Target object not found for selected target id',
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_204_NO_CONTENT)

            try:
                target.delete()
                ftp = FTP_Client()
                ftp.login()
                check = ftp.delete_dir_file(gtr)
                response = {
                    'message': 'Target Deleted Successfully',
                    'status': True,
                    'result': check
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_200_OK)

            except Exception as e:
                response = {
                    'message': str(e),
                    'status': False,
                    'result': None
                }
                publisher_obj.publish(response)
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params Missing',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)


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


class MyPaginator(pagination.LimitOffsetPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000


class TargetResponse(viewsets.ViewSet):
    """
    Viewset for Generic target add, delete, update and list
    """

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return KeybaseTargetListSerializer
        return KeybaseTargetListSerializer

    authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (DjangoModelPermissions, IsAuthenticated,)

    @action(detail=True, methods=['POST'])
    def delete_response_hdfs(self, request):
        user = request.user
        print("Request By User: ", user)
        data_dict = request.data.copy()
        keys = [*data_dict]
        if set(keys) == {'gtr'}:
            gtr = data_dict['gtr']
            try:
                specific_object = SocialTarget.objects.filter(GTR=gtr).first()
                if gtr:
                    hdfs_app_directory = 'Osint/asd'
                    file_name = "{0}.json".format(gtr)
                    delete_flag = delete_file_hdfs(
                        dir_to_store="{0}/".format(hdfs_app_directory),
                        file_name=file_name)
                    print(delete_flag)
                else:
                    delete_flag = False
                response = {'message': 'deleted',
                            'status': True,
                            'result': delete_flag}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_200_OK)
            except Exception as E:
                response = {'message': 'Error while Getting Response',
                            'status': True,
                            'result': str(E)}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'message': 'Data Keys Missing ',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def delete_response_es(self, request):
        user = request.user
        print("Request By User: ", user)
        data_dict = request.data.copy()
        keys = [*data_dict]
        if set(keys) == {'gtr'}:
            gtr = data_dict['gtr']
            try:
                specific_object = SocialTarget.objects.filter(GTR=gtr).first()
                if gtr:
                    index_string = get_index_to_delete_doc(gtr)
                    deleted = es_object.delete_document(index=index_string, gtr=gtr)
                    if deleted:
                        print("Successfully")
                    else:
                        print("Error")
                else:
                    deleted = False
                response = {'message': 'deleted',
                            'status': True,
                            'result': deleted}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_200_OK)
            except Exception as E:
                import traceback
                print(traceback.print_exc())
                response = {'message': 'Error while Getting Response',
                            'status': True,
                            'result': str(E)}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'message': 'Data Keys Missing ',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['GET'])
    def link_analysis_explore(self, request, *args, **kwargs):
        user = request.user
        print(kwargs)
        print("Request By User: ", user)
        de_serialize = TargetLinkAnalysisResponseSerializer(data=kwargs)
        print('.....................')
        de_serialize.is_valid(raise_exception=True)
        data_dict = dict(kwargs)
        keys = [*data_dict]
        es_clean.config_link_analysis['analysis'] = []
        if set(keys) == {'gtr'}:
            gtr = kwargs['gtr']
            try:
                specific_object = SocialTarget.objects.filter(GTR=gtr).first()
                if gtr:
                    alpha_gtr = specific_object.GTR
                    res = es_clean.link_analysis_explore(alpha_gtr, specific_object)
                else:
                    cleaned_responses = None
                response = {'message': 'Target_response',
                            'status': True,
                            'result': res}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_200_OK)
            except Exception as E:
                import traceback
                response = {'message': 'Error while Getting Response',
                            'status': True,
                            'result': str(E)}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'message': 'Data Keys Missing ',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def link_analysis(self, request):
        user = request.user
        print("Request By User: ", user)
        de_serialize = TargetLinkAnalysisResponseSerializer(data=request.data)
        de_serialize.is_valid(raise_exception=True)
        data_dict = request.data.copy()
        keys = [*data_dict]
        es_clean.config_link_analysis['analysis'] = []
        es_clean.set_of_gtr = []
        es_clean.flag = True
        if set(keys) == {'gtr'}:
            gtr = data_dict['gtr']
            try:
                specific_object = SocialTarget.objects.filter(GTR=gtr).first()
                if gtr:
                    alpha_gtr = specific_object.GTR
                    es_clean.link_analysis_recursion(alpha_gtr, specific_object)
                else:
                    cleaned_responses = None
                response = {'message': 'Target_response',
                            'status': True,
                            'result': es_clean.config_link_analysis}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_200_OK)
            except Exception as E:
                import traceback
                print(traceback.print_exc())
                response = {'message': 'Error while Getting Response',
                            'status': True,
                            'result': str(E)}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'message': 'Data Keys Missing ',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response, status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['POST'])
    def get_response(self, request):
        # def get_filesize(gtr=None,target_type=None,target_subtype = None):
        #     if gtr is None:
        #             raise Exception("GTR is required")
        #     query = {
        #         "query":{
        #             "match":{
        #                 "GTR":gtr
        #             }
        #         }
        #     }
        #     header = {
        #         "Content-Type":"application/json"
        #     }
        #     response = requests.post("http://192.168.18.155:9200/{}_{}_meta_data/_search".format(target_type,target_subtype),headers=header,data=json.dumps(query))
        #     print(response)
        #     folder_size = response.json()['hits']['hits'][0]['_source']['folder_size']
        #     folder_size = str(int(folder_size) / 1000000)
        #     return folder_size

        auth_user = request.user.has_perm("target_management.can_view_details")
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        available=False
        user = request.user
        posts_message = None
        print("Request By User: ", user)
        # de_serialize = TargetResponseSerializer(data=request.data)
        # de_serialize.is_valid(raise_exception=True)
        data_dict = request.data.copy()
        keys = [*data_dict]
        if set(keys) == {'target_type', 'target_id', 'limit'} or set(keys) == {'GTR', 'limit'}:
            try:
                if 'GTR' in data_dict:
                    gtr, limit = data_dict['GTR'], data_dict['limit']
                    specific_object, target_type = get_target_object(gtr=data_dict['GTR'])

                    # try:
                    #     check = gtr.split("_")
                    #     if check[0] == 'st' and check[1] == 'tw':
                    #         get_top_ten_twitter = es_object.get_twitter_top_ten_user(gtr)

                    # except: 
                    #     pass


                    print(specific_object,"-------",target_type )
                else:
                    target_type, target_id, limit = data_dict['target_type'], data_dict['target_id'], data_dict['limit']
                    specific_object, _ = get_target_object(target_type=target_type, target_id=target_id)
                if specific_object:
                    gtr = specific_object.GTR
                    target_type_es, target_sub_type_es = get_attribute(target_type=specific_object.target_type,
                                                                       sub_target_type=specific_object.target_sub_type)
                    try:
                        # print("file_size_for_GTR :> {} is {} mb".format(gtr,get_filesize(gtr,target_type_es,target_sub_type_es)))
                        print("file_size_for_GTR :> {} is {} mb".format(gtr,es_object.get_filesize(gtr,target_type_es,target_sub_type_es)))
                    except:
                        pass

                    responses = dict()
                    if target_type == 'social':
                        index_list = INDEX_LIST
                        for index in index_list:
                            index_es = get_index_for_es(target_type_es, target_sub_type_es, str(index))
                            print('index_es---------------------------->',index_es)
                            res_list, count = es_object.get_response_by_gtr(index_es, gtr, limit)
                            responses.update({index: res_list})
                    elif target_type == 'generic':
                        index_list = GENERIC_INDEX_LIST
                        print('here')
                        for index in index_list:
                            index_es = get_index_for_es(target_type_es, target_sub_type_es, str(index))
                            res_list, count = es_object.get_response_by_gtr(index_es, gtr, limit)
                            responses.update({index: res_list})
                    elif target_type == 'keybase':
                        index_list = KEYBASE_INDEX_LIST
                        for index in index_list:
                            index_es = get_index_for_es(target_type_es, target_sub_type_es, str(index))
                            res_list, count = es_object.get_response_by_gtr(index_es, gtr, limit)
                            # res_list, count = es_object.get_response_by_gtr(index_es, gtr, limit)
                            # res_list, count = es_object.get_response_by_gtr(index_es, gtr, limit)
                            responses.update({index: res_list})
                    cleaned_responses, mined_data = clean_response(responses)
                    # print('------------------------------------->',responses)

                    # get file_size
                    

                    #for showing gtr outside
                    # try:
                    #     if 'GTR' not in cleaned_responses:
                    #         cleaned_responses["GTR"]= gtr
                    # except:
                    #     pass
                    
                    
                    #


                    if cleaned_responses:
                        try:
                            categorization, sentiments, emotions, categorization_generic = es_clean.graph_data(cleaned_responses)
                            cleaned_responses.update({'profile_categorization_count': categorization})
                            cleaned_responses.update({'profile_sentiments_count': sentiments})
                            cleaned_responses.update({'profile_emotions_count': emotions})
                            cleaned_responses.update({'profile_categorization_generic_count': categorization_generic})
                        except:
                            cleaned_responses.update({'profile_categorization_count': {}})
                            cleaned_responses.update({'profile_sentiments_count': {}})
                            cleaned_responses.update({'profile_emotions_count': {}})
                        try:
                            cleaned_word_cloud = es_clean.clean_response_cloud(mined_data)
                            list_of_words = cleaned_word_cloud['word_cloud'].split(' ')
                            unique_values = set(list_of_words)
                            cleaned_responses.update({'word_cloud': [{'tag':i,"count":list_of_words.count(i)} for i in unique_values]})
                        except:
                            cleaned_responses.update({'word_cloud': ""})

                        try:
                            cleaned_most_common_words = es_clean.clean_most_common_words(mined_data)
                            cleaned_responses.update({'most_common_words': cleaned_most_common_words['common']})
                        except:
                            cleaned_responses.update({'most_common_words': []})
                        try:
                            cleaned_most_common_words = es_clean.clean_most_common_hashtags(mined_data)
                            cleaned_responses.update({'most_used_hashtags': cleaned_most_common_words['hash_tags']})
                        except:
                            cleaned_responses.update({'most_used_hashtags': []})
                        try:
                            cleaned_most_common_words = es_clean.clean_response_summary(mined_data)
                            cleaned_responses.update({'target_summary': cleaned_most_common_words['target_summary']})
                        except:
                            cleaned_responses.update({'target_summary': []})
                        try:
                            cleaned_most_common_words = es_clean.clean_response_freq(mined_data)
                            sorted_cleaned_most_common_words =(sorted(cleaned_most_common_words['graph'], key = lambda x: x['date'])) 
                            cleaned_responses.update(
                                {'post_freq_graph1': sorted_cleaned_most_common_words})
                        except:
                            cleaned_responses.update({'post_freq_graph1': []})
                    else:
                        pass
                    result = cleaned_responses
                    try:
                        # result['top_influencer']=es_object.close_associates(gtr ,1 , target_type_es, target_sub_type_es)
                        es_object.close_associates(gtr ,1 , target_type_es, target_sub_type_es)
                    except:
                        pass    
                

                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> TOP TEN START <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
                    try:
                        
                        # check = gtr.split("_")
                        if gtr:
                            get_top_ten_domain_name = es_object.get_top_ten_domain_name(gtr)
                        # else:
                        #     gtr = result['GTR']
                        #     get_top_ten_domain_name = es_object.get_top_ten_domain_name(gtr)
                    
                    # if check[0] == 'st' and check[1] == 'tw':
                        
                    except: 
                        pass

                    try:
                        # check = gtr.split("_")
                        # if check[0] == 'st' and check[1] == 'tw':
                        #     get_top_ten_twitter = es_object.get_twitter_top_ten_user(gtr)

                        if gtr:
                            get_top_ten_twitter = es_object.get_twitter_top_ten_user(gtr)
                        # else:
                        #     gtr = result['GTR']
                        #     get_top_ten_twitter = es_object.get_twitter_top_ten_user(gtr)

                    except: 
                        pass

                    try:
                        result['get_top_ten_domain_name'] = get_top_ten_domain_name
                    except:
                        pass

                    try:
                        result['top_influencers'] = get_top_ten_twitter
                    except:
                        pass
                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> TOP TEN END <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

                    if 'st' in gtr:
                        crawled_posts = len(result['posts'])
                        social_target_obj = SocialTarget.objects.get(GTR=gtr)
                        user_entered_posts = social_target_obj.max_posts
                        operations_details = SocialTarget.objects.get(GTR=gtr)
                        target_date = social_target_obj.created_on
                        result['operations'] = operations_details.operations
                        result['target_posts'] = user_entered_posts
                        result['total_crawled_posts'] = crawled_posts
                    if 'kb' in gtr:
                        obj = KeybaseTarget.objects.get(GTR=gtr)
                        result['keybase_title'] = obj.keybase_title
                        result['created_on'] = obj.created_on
                        keybase_id = obj.keybase_id
                        keybase_obj = Keybase.objects.get(id=keybase_id)
                        result['keywords'] = keybase_obj.keywords
                        result['mentions'] = keybase_obj.mentions
                        result['hashtags'] = keybase_obj.hashtags
                        result['phrases'] = keybase_obj.phrases

                    if 'gn' in gtr:
                        obj = GenericTarget.objects.get(GTR=gtr)
                        result['keybase_title'] = obj.title
                    
                    try:
                        user_active_hours = {i:0  for i in range(25)}
                        # print(user_active_hours)
                        # print("resutl------------")
                        month = []
                        frequency = {}
                        for each_post in result['posts']:
                            try:
                                hour = datetime.datetime.fromtimestamp(each_post['timestamp_c']).strftime('%H:%M:%S').split(":")[0]
                                # month.append(datetime.datetime.fromtimestamp(each_post['timestamp_c']).strftime('%m/%d/%Y')) 
                                month.append(each_post['timestamp_c'])
                                user_active_hours[int(hour)] = user_active_hours[int(hour)] + 1
                                # frequency[str(month)] = month
                            except:
                                pass
                    except:
                        pass

                    user_posts_data = [ {"hours":key, "posts":values }  for key, values in user_active_hours.items()]
                    result["user_posts_data"] = user_posts_data

                    
                    try:
                        is_picture = {"category":"picture",'true':0, "false":0}
                        is_shared = {"category":"shared",'true':0, "false":0}
                        is_text = {"category":"text",'true':0, "false":0}
                        is_video = {"category":"video",'true':0, "false":0}
                        is_tweeted = {"category":"retweet",'true':0, "false":0}
                        for each_post in result['posts']:
                            check_gtr = each_post['GTR'].split("_")
                            if check_gtr[1] == "rd" or check_gtr[1] == "in" or check_gtr[1] == "tw" or check_gtr[1] == "ln":

                                try:
                                    if len(each_post['text_c']) >= 2:
                                        is_text['true'] = is_text['true'] + 1
                                    else:
                                        is_text['false'] = is_text['false'] + 1
                                except:
                                    pass

                                
                                try:
                                    if len(each_post['media_c']) != 0:
                                        is_picture['true'] = is_picture['true'] + 1
                                    else:
                                        is_picture['false'] = is_picture['false'] + 1
                                except:
                                    pass

                                try:
                                    if each_post['is_retweet'] == True:
                                        is_tweeted['true'] = is_tweeted['true'] + 1
                                    else:
                                        is_tweeted['false'] = is_tweeted['false'] + 1
                                except:
                                    pass

                            else:
                                try:
                                    if each_post['content_type']['is_picture'] == True:
                                        is_picture['true'] = is_picture['true'] + 1
                                    else:
                                        is_picture['false'] = is_picture['false'] + 1
                                except:
                                    pass

                                try:
                                    if each_post['content_type']['is_shared'] == True:
                                        is_shared['true'] = is_shared['true'] + 1
                                    else:
                                        is_shared['false'] = is_shared['false'] + 1
                                except:
                                    pass

                                try:
                                    if each_post['content_type']['is_text'] == True:
                                        is_text['true'] = is_text['true'] + 1
                                    else:
                                        is_text['false'] = is_text['false'] + 1
                                except:
                                    pass

                                    
                                try:
                                    if each_post['content_type']['is_video'] == True:
                                        is_video['true'] = is_video['true'] + 1
                                    else:
                                        is_video['false'] = is_video['false'] + 1
                                except:
                                    pass

                        try:
                            result['average_engagment_per_posts'] = [is_picture,is_shared,is_text,is_video,is_tweeted]
                        except:
                            result['average_engagment_per_posts'] = None
                         
                    except :
                        pass

                    # try:
                    #     is_picture = {"category":"picture",'true':0, "false":0}
                    #     is_text = {"category":"text",'true':0, "false":0}
                    #     for each_post in result['posts']:
                    #         print("-----------------------------<<<< ",each_post['text_c'])
                    #         try:
                                
                    #             if len(each_post['text_c']) >= 2:
                    #                 is_text['true'] = is_text['true'] + 1
                    #             else:
                    #                 is_text['false'] = is_text['false'] + 1
                    #         except:
                    #             pass


                    #         try:
                    #             if each_post['media_c']:
                    #                 is_picture['true'] = is_picture['true'] + 1
                    #             else:
                    #                 is_picture['false'] = is_picture['false'] + 1
                    #         except:
                    #             pass

                    #     try:
                    #         result['average_engagment_per_posts'] = [is_picture,is_text]
                    #     except:
                    #         result['average_engagment_per_posts'] = None
                    # except:
                    #     pass

                    

                    try:
                        montha = sorted(month)
                        month1 = [datetime.datetime.fromtimestamp(date).strftime('%Y-%m-%d') for date in montha]
                        count_month = {}
                        for date in month1:
                            if date in count_month:
                                count_month[str(date)] = count_month[str(date)] + 1
                            else:
                                count_month[str(date)] = 1


                        month = [{"frequency":value, "date":key} for key, value in count_month.items()]
                        # unique_month = set(month1)

                        # month2 = [{"data":date, "frequency":month1.count(date)} for date in unique_month]
                        # sorted_cleaned_most_common_words =(sorted(month2, key = lambda x: x['date'])) 
                        result['post_freq_graph'] = month
                    except :
                         result['post_freq_graph'] = None

                else:
                    result = None

                def target_contributors(gtr):

                    result={}
                    latest_date_list=[]
                    
                    try:
                        # gtr=kwargs['gtr']
                        gtrsplit=gtr.split('_')
                        if gtrsplit[0]=='dt' :
                            contributors_generic=[]
                            generic_target_marked=GenericTarget.objects.filter(GTR=gtr).first()
                            generic_target_id_get=generic_target_marked.id
                            try:
                                result['created_by']=generic_target_marked.user.username
                                result['created_on']=generic_target_marked.created_on
                            except :
                                pass    
                            generic_generated_report=Log.objects.filter(request_url='/v1/target/get/response/')
                            generic_generated_report=LogSerializersversion2(generic_generated_report,many=True)
                            generic_generated_report_json_data=JSONRenderer().render(generic_generated_report.data)
                            generic_generated_report_data = json.loads(generic_generated_report_json_data)
                            for each_data in generic_generated_report_data:
                                try:
                                    dict_for_generic={}
                                    if each_data['request_data']['target_type']=='generic' and  each_data['request_data']['target_id']==str(generic_target_id_get) :
                                            report_username=User.objects.filter(id=each_data['request_username']).first()     
                                            dict_for_generic['report_generated_by']=report_username.username
                                            dict_for_generic['report_generated_on']=each_data['request_time']
                                            contributors_generic.append(dict_for_generic)
                                            result['report_generated']=contributors_generic
                                            # print('report_--------------------->genreated')                      
                                    else:
                                        pass
                                except Exception as e:
                                    print('alert',e)
                            unique_listgen=[]        
                                
                            for each in contributors_generic:
                                unique_listgen.append(each['report_generated_by'])
                            unique_operationgen=len(set(unique_listgen))
                            result['total contributors']=unique_operationgen         
                        else:
                            
                            if gtrsplit[0]=='kb':
                                contributors_keybase=[]
                                keybase_target_marked=KeybaseTarget.objects.filter(GTR=gtr).first()
                                try:
                                    result['created_by']=keybase_target_marked.user.username
                                    result['created_on']=keybase_target_marked.created_on
                                except :
                                    pass    
                                keybase_generated_report=Log.objects.filter(request_url='/v1/report/get/notes/')
                                keybase_generated_report=LogSerializersversion2(keybase_generated_report,many=True)
                                keybase_generated_report_json_data=JSONRenderer().render(keybase_generated_report.data)
                                keybase_generated_reportjson_data = json.loads(keybase_generated_report_json_data)
                                    
                                for each_data in keybase_generated_reportjson_data:
                                    try:
                                        dict_for_keybase={}
                                        if each_data['request_data']['type']=='keybase' and  each_data['request_data']['report_id']==gtr :
                                                report_username=User.objects.filter(id=each_data['request_username']).first()     
                                                dict_for_keybase['report_generated_by']=report_username.username
                                                dict_for_keybase['report_generated_on']=each_data['request_time']
                                                contributors_keybase.append(dict_for_keybase)
                                                result['report_generated']=contributors_keybase
                                                # print('report_--------------------->genreated')                      
                                        else:
                                            pass
                                    except Exception as e:
                                        # print(e)
                                        pass
                                unique_listkey=[]        
                                    
                                for each_name2 in contributors_keybase:
                                    unique_listkey.append(each_name2['report_generated_by'])
                                unique_operationkey=len(set(unique_listkey))
                                result['total_contributors']=unique_operationkey        

                                
                            elif gtrsplit[0]=='st':
                                    contributors=[]
                                    operation=[]
                                
                                    social_target_marked=SocialTarget.objects.filter(GTR=gtr).first()
                                    try:
                                        result['created_by']=social_target_marked.user.username
                                        result['created_on']=social_target_marked.created_on
                                    except:
                                        pass    
                                    generated_report=Log.objects.filter(request_url='/v1/report/get/notes/')
                                    generated_report=LogSerializersversion2(generated_report,many=True)
                                    generated_report_json_data=JSONRenderer().render(generated_report.data)
                                    generated_reportjson_data = json.loads(generated_report_json_data)
                                    for each_date in generated_reportjson_data:
                                        try:
                                            if each_date['request_data']['type']=='targetDetail' and  each_date['request_data']['report_id']==gtr:
                                                date_latest=each_date['request_time']
                                                latest_date_list.append(date_latest)
                                        except Exception as e:
                                            # print(e)    
                                            pass        
                                    
                                    for each_data in generated_reportjson_data:
                                        try:
                                            new_dict_contributors={}
                                            if each_data['request_data']['type']=='targetDetail' and  each_data['request_data']['report_id']==gtr:
                                                    report_username=User.objects.filter(id=each_data['request_username']).first()     
                                                    new_dict_contributors['report_generated_by']=report_username.username
                                                    new_dict_contributors['report_generated_on']=each_data['request_time']
                                                    contributors.append(new_dict_contributors)
                                                    result['contributors']=contributors
                                                    # print('report_--------------------->genreated')                      
                                            else:
                                                pass
                                        except Exception as e:
                                            # print(e)
                                            pass
                                    json_data_operation = Log.objects.filter(request_url="/v1/target/set/response/")
                                    operation_detail=LogSerializersversion2(json_data_operation,many=True)
                                    json_operation_detail=JSONRenderer().render(operation_detail.data)
                                    final_json_operation_detail = json.loads(json_operation_detail)
                                    # for each_date in final_json_operation_detail:
                                    #     try:
                                    #         if each_date['request_data']['target_type']=='social' and  each_date['request_data']['GTR']==gtr:
                                    #             date_latest_operation=each_date['request_time']
                                    #             latest_date_list2.append(date_latest_operation)
                                    #     except Exception as e:
                                    #         print(e)  
                                    for each_data in final_json_operation_detail:
                                        try:
                                            new_dict_for_operation={}
                                            if each_data['request_data']['GTR']==gtr and  each_data['request_data']['target_type']=='social' :
                                                    report_username=User.objects.filter(id=each_data['request_username']).first()     
                                                    new_dict_for_operation['operation_by']=report_username.username
                                                    new_dict_for_operation['operation_on']=each_data['request_time']
                                                    # print('report_--------------------->genreated')         
                                                    operation.append(new_dict_for_operation)    
                                                    result['operations']=operation    

                                            else:
                                                pass
                                            

                                        except Exception as e:
                                            # print(e)
                                            pass
                                    unique_list=[]        
                                    for each_name in operation:
                                        unique_list.append(each_name['operation_by'])
                                    unique_operation=len(set(unique_list))
                                    unique_list2=[]        
                                    for each_name2 in contributors:
                                        unique_list2.append(each_name2['report_generated_by'])
                                    unique_operation2=len(set(unique_list2))
                                    result['total_contributors']=unique_operation+unique_operation2
                                    return result
                    except:
                        pass

                try:
                    result['target_contributors'] = target_contributors(gtr)
                except:
                    gtr = result['GTR']
                    result['target_contributors']  = target_contributors(gtr)


                try:
                    for each_post in result['posts']:
                        each_post['id'] = str(each_post['id'])
                    sorted_posts = sorted(result['posts'], key = lambda i: i['created_on'],reverse=True)
                    result['posts'] = sorted_posts
                except:
                    pass
                list_of_engines=[]
                   
                try:
                    for each_engine_bing in result['search_engine_bing'][0]['results']:
                        if each_engine_bing['status']=="800":
                            each_engine_bing['engine_name']='bing'
                            # print('------------------bing')
                            list_of_engines.append(each_engine_bing)
                        else:
                            pass  
                except:
                    pass    

                try:   
                    for each_engine_ask in result['search_engine_ask'][0]['results']:
                        if each_engine_ask['status']=="800":
                            each_engine_ask['engine_name']='ask'
                            # print('------------------ask')
                            list_of_engines.append(each_engine_ask)
                        else:
                            pass
                except:
                    pass

                try:
                    for each_engine_baidu in result['search_engine_baidu'][0]['results']:
                        if each_engine_baidu['status']=="800":
                            each_engine_baidu['engine_name']='baidu'
                            # print('------------------baidu')
                            list_of_engines.append(each_engine_baidu)
                        else:
                            pass
                except:
                    pass
                     
                try:     
                    for each_engine_duckduckgo in result['search_engine_duckduckgo'][0]['results']:
                        if each_engine_duckduckgo['status']=="800":
                            each_engine_duckduckgo['engine_name']='duckduckgo'
                            # print('------------------duckduckgo')
                            list_of_engines.append(each_engine_duckduckgo)
                        else:
                            pass           
                except:
                    pass        

                try:
                    for each_engine_google in result['search_engine_google'][0]['results']:
  
                        if each_engine_google['status']=="800":
                            each_engine_google['engine_name']='google'
                            # print('------------------google')
                            list_of_engines.append(each_engine_google)
                        else:
                            pass
                except:
                    pass  
                try:
                    for each_engine_yahoo in result['search_engine_yahoo'][0]['results']:
                        if each_engine_yahoo['status']=="800":
                            each_engine_yahoo['engine_name']='yahoo'
                            # print('------------------yahoo')
                            list_of_engines.append(each_engine_yahoo)
                        else:
                            pass  
                except:
                    pass   
                try:        
                    for each_engine_yandex in result['search_engine_yandex'][0]['results']:
                        if each_engine_yandex['status']=="800":
                            each_engine_yandex['engine_name']='yandex'
                            # print('------------------yandex')
                            list_of_engines.append(each_engine_yandex)
                        else:
                            pass            
                except:
                    pass
                twitter_list=[]
                twitter_posts = []
                try:
                    for each_twitter_data in result['twitter_tweets']:
                        for each_user in each_twitter_data['users']:
                            twitter_list.append(each_user)

                        for each_post in each_twitter_data['posts']:
                            twitter_posts.append(each_post)

                except:
                    pass

                result['twitter_list_user']=twitter_list
                result['twitter_list_posts']=twitter_posts
                result['search_engine_failed']=list_of_engines

                # if result['target_posts']==result['total_crawled_posts']:
                #     available=True
                # else:
                #     available=False        

                try:
                    news_dic = {
                        'ary':[],
                        'bbc.':[],
                        'geo':[],
                        'ndtv.':[],
                        'zee.':[],
                        'abp':[],
                        'dawn':[],
                        'indiatoday':[]

                    }
                    #code for dinamic 
                    # for each_news in result['news_data']:
                    #     if each_news['title'] not in news_dic:
                    #         news_dic[each_news['title']] = [each_news]
                    #     else:
                    #         news_dic[each_news['title']].append(each_news) 

                    for each_news in result['news_data']:
                        for each_key in news_dic.keys():
                            each_key_=each_key.replace('.',"")
                            if each_news['href'].find(each_key_)!=-1:
                                news_dic[each_key].append(each_news)
                            else:
                                pass

                            

                except Exception as e:
                    pass

                
                try:
                    if result['facebook_posts']:
                        for response_data in responses['facebook_posts']:
                            for each_result_post in result['facebook_posts']:
                                if str(response_data['es_id']) == str(each_result_post['es_id']) :
                                    each_result_post['author'] = response_data['author']
                except Exception as e:
                    print("exceptions", e)
                    # pass

                # print(news_dic)
                result["news_data_filtered"]= news_dic
                try:
                    result['target_id'] = target_id
                except:
                    pass
                print(type(result))
                response = {'message': 'Target_response',
                            'status': True,
                            'result': result, 
                            'available':available
                            }
                return Response(response, status=status.HTTP_200_OK)
            except Exception as E:
                response = {'message': 'Error while Getting Response',
                            'status': True,
                            'result': str(E)}
                publisher_obj.publish(response)
                return Response(response, status=status.HTTP_204_NO_CONTENT)
        else:
            response = {
                'message': 'Data Keys Missing ',
                'status': False,
                'result': None
            }
            publisher_obj.publish(response)
            return Response(response, status=status.HTTP_204_NO_CONTENT)
  
    @action(detail=True, methods=['POST'])
    def target_response(self, request):
        auth_user = request.user.has_perm("target_management.can_perform_operations")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        if request.data is not None:
            print('*********************all-operations***************', request.data)
            try:
                gtr = request.data['GTR']
                target = request.data['target_type']
                action = request.data['action']
                # all_operations = request.data['all_operations']
            except Exception as error:
                response = {
                    'message': 'Arguments Error'
                }
                return Response(response)

            # print('-----------------------', social_target_obj.operations)
            if gtr:
                try:
                    if target == 'social':
                        target_object = SocialTarget.objects.get(GTR=gtr)
                        ctr_id = target_object.CTR
                        target_type, target_subtype = get_attribute(target_type=target_object.target_type,
                                                                    sub_target_type=target_object.target_sub_type)

                    elif target == 'generic':
                        target_object = GenericTarget.objects.get(GTR=gtr)
                        ctr_id = target_object.CTR
                        target_type, target_subtype = get_attribute(target_type=target_object.target_type,
                                                                    sub_target_type=target_object.target_sub_type)

                    elif target == 'keybase':
                        target_object = KeybaseTarget.objects.get(GTR=gtr)
                        ctr_id = target_object.CTR
                        target_type, target_subtype = get_attribute(target_type=target_object.target_type,
                                                                    sub_target_type=target_object.target_sub_type)

                    else:
                        gtr, ctr_id, target_type, target_subtype = None, None, None, None
                        target_object = None

                    if action == 'sentiment_analysis':
                        response = bds_object.sentiment_analysis(gtr, ctr_id, target_type, target_subtype)
                    # elif action == 'change_detection':
                    #     response = bds_object.change_detection(gtr, ctr_id, target_type, target_subtype)
                    # elif action == 'behaviour_analysis':
                    #     response = bds_object.behavior_analysis(gtr, ctr_id, target_type, target_subtype)
                    elif action == 'emotions_analyst':
                        response = bds_object.emotions_analyst(gtr, ctr_id, target_type, target_subtype)
                    elif action == 'text_categorization':
                        response = bds_object.text_categorization(gtr, ctr_id, target_type, target_subtype)
                    elif action == 'target_summary':
                        response = bds_object.target_summary(gtr, ctr_id, target_type, target_subtype)
                    elif action == 'word_cloud':
                        response = bds_object.word_cloud(gtr, ctr_id, target_type, target_subtype)
                    elif action == 'posts_frequent_graph':
                        response = bds_object.posts_frequent_graph(gtr, ctr_id, target_type, target_subtype)
                    elif action == 'frequent_hashtags':
                        response = bds_object.frequent_hashtags(gtr, ctr_id, target_type, target_subtype)
                    elif action == 'common_words':
                        response = bds_object.common_words(gtr, ctr_id, target_type, target_subtype)

                    else:
                        response = None

                    final_response = {
                        'status': str(response)
                    }

                    target_object.operations[action] = True
                    SocialTarget.objects.filter(GTR=gtr).update(operations=target_object.operations)
                    if response.status_code == 201:
                        # social_target_obj = SocialTarget.objects.get(GTR=gtr)
                        # social_target_obj.operations[action] = True
                        # social_target_obj.save()
                        # print('****************************', social_target_obj.operations)
                        # operations_dict = dict(target_object.operations)
                        # operations_dict.update({action: True})
                        # print('------------', operations_dict)
                        # setattr(target_object, 'operations', operations_dict)
                        # a = target_object.update()
                        # print('---------------', a)
                        return Response(final_response, status=status.HTTP_201_CREATED)
                    else:
                        return Response(final_response, status=status.HTTP_400_BAD_REQUEST)
                except Exception as error:
                    response = {
                        'message': "Error",
                        'status': False,
                        'result': str(error)
                    }
                    return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        response = {
            'message': "Not Found",
            'status': False,
            'result': None
        }
        publisher_obj.publish(response)

        return Response(response, status=status.HTTP_409_CONFLICT)

    @action(detail=True, methods=['POST'])
    def response_by_id(self, request):
        try:
            es_id = request.data['id']

        except Exception as error:
            response = {
                "message": "Id error"
            }
            return Response(response, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        try:
            responses = es_object.get_response_id(es_id)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
        response = {
            "result": responses
        }

        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def get_posts(self, request):
        auth_user = request.user.has_perm("core_management.history_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        try:
            data_dict = request.data.copy()
            keys = [*data_dict]
            if set(keys) == {'lte', 'gte'} or set(keys) == {'lte', 'gte', 'gtr'}:
                start_point = int(data_dict['lte'])
                gte = int(data_dict['gte'])
                next_len = gte - start_point
                if 'gtr' in data_dict:
                    gtr = data_dict['gtr']
                    responses = list(es_object.get_posts_by_gtr(gtr=gtr, lte=start_point, size=next_len)[0])
                    for idx in range(len(responses)):
                        responses[idx].update({'headline': responses[idx]['posts']['headline']})
                else:
                    responses = list(es_object.get_all_posts(lte=start_point, size=next_len)[0])
                    for idx in range(len(responses)):
                        if 'posts' in responses[idx]:
                            if 'headline' in responses[idx]['posts']:
                                responses[idx].update({'headline': responses[idx]['posts']['headline']})
                            else:
                                pass
                        else:
                            pass
            else:
                responses = None
            return Response(responses, status=status.HTTP_200_OK)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def get_followers(self, request):
        try:
            data_dict = request.data.copy()
            keys = [*data_dict]
            if set(keys) == {'lte', 'gte'} or set(keys) == {'lte', 'gte', 'gtr'}:
                start_point = int(data_dict['lte'])
                gte = int(data_dict['gte'])
                next_len = gte - start_point
                print(start_point)
                print(next_len)
                if 'gtr' in data_dict:
                    gtr = data_dict['gtr']
                    print(gtr)
                    responses = list(es_object.get_followers_by_gtr(gtr=gtr, lte=start_point, size=next_len)[0])
                else:
                    responses = list(es_object.get_all_followers(lte=start_point, size=next_len)[0])
            else:
                responses = None
            return Response(responses, status=status.HTTP_200_OK)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def get_following(self, request):
        try:
            data_dict = request.data.copy()
            keys = [*data_dict]
            if set(keys) == {'lte', 'gte'} or set(keys) == {'lte', 'gte', 'gtr'}:
                start_point = int(data_dict['lte'])
                gte = int(data_dict['gte'])
                next_len = gte - start_point
                print(start_point)
                print(next_len)
                if 'gtr' in data_dict:
                    gtr = data_dict['gtr']
                    responses = list(es_object.get_followings_by_gtr(gtr=gtr, lte=start_point, size=next_len)[0])
                else:
                    responses = list(es_object.get_all_followings(lte=start_point, size=next_len)[0])
            else:
                responses = None
            return Response(responses, status=status.HTTP_200_OK)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)


    
    @action(detail=True, methods=['POST'])
    def target_share_resource(self, request):
        TargetShareResourceSerializer()
        serializer = TargetShareResourceSerializer(data=request.data)
        if serializer.is_valid():

            target_type = serializer.data['target_type']

            print("target_type", target_type)
            # serializer.save()
            if target_type == "social":
                target =  SocialTarget.objects.get(id= serializer.data['target_id'])
            elif target_type == "generic":
                target = GenericTarget.objects.get(id= serializer.data['target_id'])
            elif target_type == "keybase":
                target = KeybaseTarget.objects.get(id=serializer.data['target_id'])
            elif target_type == "case":
                target = Case.objects.get(id=serializer.data['target_id'])
            elif target_type == "individual":
                target = Individual.objects.get(id=serializer.data['target_id'])
            elif target_type == "group":
                target = Group.objects.get(id=serializer.data['target_id'])
            elif target_type == "event":
                target = Event.objects.get(id=serializer.data['target_id'])

            if target:
                a = target.share_resource
                a.append(serializer.data['user'])
                target.update()
            else:
                return Response({"message":"Share resource not found","results":[]}, status=201)    
            return Response({"message":"Successfully Share","results":[serializer.data]}, status=201)
        return Response({"message":serializer.errors,"results":[]}, status=400)
        
    


class SocialMediaAccount(viewsets.ModelViewSet):
    authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (DjangoModelPermissions, IsAuthenticated,)
    serializer_class = SocialMediaAccountSettings

    def list(self, request, *args, **kwargs):
        
        if request.user.is_superuser :
            try:
                data = ess_object.getall_sm_account()
                print(data['accounts'])
            except Exception as e:
                print('---------------', e, '----------dt_gn_969----')
                return Response({"result": "No data found "})
            return Response({"result": data['accounts']})
        else:
            response = {
                'message': 'permission not given missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
                
    def create(self, request, *args, **kwargs):
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
            print(request.data['username'], " dataaaa ")
            data1 = ess_object.add_sm_account(social_media=request.data['social_media'],
                                             username=request.data['username'],
                                             status=request.data['status'], email=request.data['email'],
                                             password=request.data['password'], userid=request.data['userid'])
            print(data1, 'is data') 
        except Exception as e:
            print('------------', e, '------------')
            pass
        return Response(data1)

    def update(self, request, *args, **kwargs):
        try:
            print(request.data['username'], " dataaaa ")
            data = ess_object.update_sm_account(social_media=request.data['social_media'],
                                                username=request.data['username'],
                                                status=request.data['status'], email=request.data['email'],
                                                password=request.data['password'], userid=request.data['userid'])
            print(data, 'is data')
        except Exception as e:
            print('------------', e, '------------')
        return Response(data)

    def destroy(self, request, *args, **kwargs):
        try:
            print(request.data)
            data = ess_object.delete_sm_account(userid=request.data['userid'])
            print(data, 'is data')

        except Exception as e:
            print('------------', e, '------------')

        return Response(data)
      
    def target_contributors(self,request,**kwargs):
        result={}
        latest_date_list=[]
        latest_date_list2=[]
        latest_date_list3=[]
        try:
            gtr=kwargs['gtr']
            gtrsplit=gtr.split('_')
            # gtr_type=gtr.isdigit()
            if gtrsplit[0]=='dt' :
                contributors_generic=[]
                generic_target_marked=GenericTarget.objects.filter(GTR=gtr).first()
                generic_target_id_get=generic_target_marked.id
                try:
                    result['created_by']=generic_target_marked.user.username
                    result['created_on']=generic_target_marked.created_on
                except :
                    pass    
                generic_generated_report=Log.objects.filter(request_url='/v1/target/get/response/')
                generic_generated_report=LogSerializersversion2(generic_generated_report,many=True)
                generic_generated_report_json_data=JSONRenderer().render(generic_generated_report.data)
                generic_generated_report_data = json.loads(generic_generated_report_json_data)
                for each_data in generic_generated_report_data:
                    try:
                        dict_for_generic={}
                        if each_data['request_data']['target_type']=='generic' and  each_data['request_data']['target_id']==str(generic_target_id_get) :
                                report_username=User.objects.filter(id=each_data['request_username']).first()     
                                dict_for_generic['report_generated_by']=report_username.username
                                dict_for_generic['report_generated_on']=each_data['request_time']
                                contributors_generic.append(dict_for_generic)
                                result['report_generated']=contributors_generic
                                # print('report_--------------------->genreated')                      
                        else:
                            pass
                    except Exception as e:
                        print('alert',e)
                unique_listgen=[]        
                    # for each_name in operation:
                    #     unique_list.append(each_name['operation_by'])
                    # unique_operation=len(set(unique_list))
                    # unique_list2=[]        
                for each in contributors_generic:
                    unique_listgen.append(each['report_generated_by'])
                unique_operationgen=len(set(unique_listgen))
                result['total contributors']=unique_operationgen         
            else:
                
                if gtrsplit[0]=='kb':
                    contributors_keybase=[]
                    keybase_target_marked=KeybaseTarget.objects.filter(GTR=gtr).first()
                    try:
                        result['created_by']=keybase_target_marked.user.username
                        result['created_on']=keybase_target_marked.created_on
                    except :
                        pass    
                    keybase_generated_report=Log.objects.filter(request_url='/v1/report/get/notes/')
                    keybase_generated_report=LogSerializersversion2(keybase_generated_report,many=True)
                    keybase_generated_report_json_data=JSONRenderer().render(keybase_generated_report.data)
                    keybase_generated_reportjson_data = json.loads(keybase_generated_report_json_data)
                    # for each_date in keybase_generated_reportjson_data:
                    #     try:
                    #         if each_date['request_data']['type']=='keybase' and  each_date['request_data']['report_id']==gtr:
                    #             date_latest=each_date['request_time']
                    #             latest_date_list.append(date_latest)
                    #     except Exception as e:
                    #         print(e)    
                    for each_data in keybase_generated_reportjson_data:
                        try:
                            dict_for_keybase={}
                            if each_data['request_data']['type']=='keybase' and  each_data['request_data']['report_id']==gtr :
                                    report_username=User.objects.filter(id=each_data['request_username']).first()     
                                    dict_for_keybase['report_generated_by']=report_username.username
                                    dict_for_keybase['report_generated_on']=each_data['request_time']
                                    contributors_keybase.append(dict_for_keybase)
                                    result['report_generated']=contributors_keybase
                                    # print('report_--------------------->genreated')                      
                            else:
                                pass
                        except Exception as e:
                            # print(e)
                            pass
                    unique_listkey=[]        
                        # for each_name in operation:
                        #     unique_list.append(each_name['operation_by'])
                        # unique_operation=len(set(unique_list))
                        # unique_list2=[]        
                    for each_name2 in contributors_keybase:
                        unique_listkey.append(each_name2['report_generated_by'])
                    unique_operationkey=len(set(unique_listkey))
                    result['total contributors']=unique_operationkey        

                    # json_data_operation = Log.objects.filter(request_url="/v1/target/set/response/")
                    # operation_detail=LogSerializersversion2(json_data_operation,many=True)
                    # json_operation_detail=JSONRenderer().render(operation_detail.data)
                    # final_json_operation_detail = json.loads(json_operation_detail)
                    # for each_date in final_json_operation_detail:
                    #     try:
                    #         if each_date['request_data']['target_type']=='social' and  each_date['request_data']['GTR']==gtr:
                    #             date_latest_operation=each_date['request_time']
                    #             latest_date_list3.append(date_latest_operation)
                    #     except Exception as e:
                    #         print(e)  
                    # for each_data in final_json_operation_detail:
                    #     try:
                    #         if each_data['request_data']['GTR']==gtr and  each_data['request_data']['target_type']=='social' :
                    #                 report_username=User.objects.filter(id=each_data['request_username']).first()     
                    #                 result['operation_by']=report_username.username
                    #                 result['operation_on']=each_data['request_time']
                    #                 print('operation_--------------------->genreated')                      
                    #         else:
                    #             pass
                    #     except Exception as e:
                    #         print(e)

                elif gtrsplit[0]=='st':
                        contributors=[]
                        operation=[]
                    
                        social_target_marked=SocialTarget.objects.filter(GTR=gtr).first()
                        try:
                            result['created_by']=social_target_marked.user.username
                            result['created_on']=social_target_marked.created_on
                        except:
                            pass    
                        generated_report=Log.objects.filter(request_url='/v1/report/get/notes/')
                        generated_report=LogSerializersversion2(generated_report,many=True)
                        generated_report_json_data=JSONRenderer().render(generated_report.data)
                        generated_reportjson_data = json.loads(generated_report_json_data)
                        for each_date in generated_reportjson_data:
                            try:
                                if each_date['request_data']['type']=='targetDetail' and  each_date['request_data']['report_id']==gtr:
                                    date_latest=each_date['request_time']
                                    latest_date_list.append(date_latest)
                            except Exception as e:
                                # print(e)   
                                pass         
                        
                        for each_data in generated_reportjson_data:
                            try:
                                new_dict_contributors={}
                                if each_data['request_data']['type']=='targetDetail' and  each_data['request_data']['report_id']==gtr:
                                        report_username=User.objects.filter(id=each_data['request_username']).first()     
                                        new_dict_contributors['report_generated_by']=report_username.username
                                        new_dict_contributors['report_generated_on']=each_data['request_time']
                                        contributors.append(new_dict_contributors)
                                        result['contributors']=contributors
                                        # print('report_--------------------->genreated')                      
                                else:
                                    pass
                            except Exception as e:
                                # print(e)
                                pass
                        json_data_operation = Log.objects.filter(request_url="/v1/target/set/response/")
                        operation_detail=LogSerializersversion2(json_data_operation,many=True)
                        json_operation_detail=JSONRenderer().render(operation_detail.data)
                        final_json_operation_detail = json.loads(json_operation_detail)
                        # for each_date in final_json_operation_detail:
                        #     try:
                        #         if each_date['request_data']['target_type']=='social' and  each_date['request_data']['GTR']==gtr:
                        #             date_latest_operation=each_date['request_time']
                        #             latest_date_list2.append(date_latest_operation)
                        #     except Exception as e:
                        #         print(e)  
                        for each_data in final_json_operation_detail:
                            try:
                                new_dict_for_operation={}
                                if each_data['request_data']['GTR']==gtr and  each_data['request_data']['target_type']=='social' :
                                        report_username=User.objects.filter(id=each_data['request_username']).first()     
                                        new_dict_for_operation['operation_by']=report_username.username
                                        new_dict_for_operation['operation_on']=each_data['request_time']
                                        # print('report_--------------------->genreated')         
                                        operation.append(new_dict_for_operation)    
                                        result['operations']=operation    

                                else:
                                    pass
                                   

                            except Exception as e:
                                # print(e)
                                pass
                        unique_list=[]        
                        for each_name in operation:
                            unique_list.append(each_name['operation_by'])
                        unique_operation=len(set(unique_list))
                        unique_list2=[]        
                        for each_name2 in contributors:
                            unique_list2.append(each_name2['report_generated_by'])
                        unique_operation2=len(set(unique_list2))
                        result['total contributors']=unique_operation+unique_operation2



        except Exception as error:
            response={
                'error':str(error)
                }  
            return Response(response)        

        response={
                'message':result
            }    
        return Response(response)   
    def target_available_key(self,request,**kwargs):
        try:
            gtr=kwargs['gtr']
            gtr_type=gtr.isdigit()
            generic_status=[]
            keybase_status=[]
            social_status=[]
            available_key=False
            print("------------gtr-----------",gtr)
            gtrsplit=gtr.split('_')
            if gtrsplit[0]=='dt' :
                generic_target_marked=GenericTarget.objects.filter(GTR=gtr).first()
                print(generic_target_marked)
                generic_status=generic_target_marked.target_status_string
                generic_status_split=generic_status.split(',')
                if generic_status_split[-1]=='Successful! data store to BDS ':
                    available_key=True
                else:
                    available_key=False    

                

        
            elif gtrsplit[0]=='kb':
                keybase_target_marked=KeybaseTarget.objects.filter(GTR=gtr).first()
                keybase_status=keybase_target_marked.target_status_string
                keybase_status_split=keybase_status.split(',')
                if keybase_status_split[-1]=='Successful! data store to BDS ':
                    available_key=True
                else:
                    available_key=False    


                
            elif gtrsplit[0]=='st':
                social_target_marked=SocialTarget.objects.filter(GTR=gtr).first()
                social_status=social_target_marked.target_status_string
                social_status_split=social_status.split(',')
                if social_status_split[-1]=='Successful! data store to BDS ':
                    available_key=True
                else:
                    available_key=False    


        

            
        except Exception as error:
            response={
                'message':str(error)
            }     
            return Response(response)

        response={
                'result':available_key
            }     
        return Response(response)


       

class PeriodicTarget(viewsets.ViewSet):
    authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (DjangoModelPermissions, IsAuthenticated,)

    def all_periodic_targets(self, request):
        generic_target = GenericTarget.objects.filter(user=request.user).values()
        social_target = SocialTarget.objects.filter(user=request.user).values()
        keybase_target = KeybaseTarget.objects.filter(user=request.user).values()

        all_targets = {'generic_targets': generic_target, 'social_targets': social_target,
                       'keybase_targets': keybase_target}

        response = {
            'result': all_targets
        }

        return Response(response)

    def update_periodic_target(self, request):
        try:
            print(request.data)
            id = request.data['id']
            action = request.data['action']
            if action == 'True':
                final_action = True
            elif action == 'False':
                final_action = False
            target_type = request.data['target_type']
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)
        try:
            if target_type == 'gn':
                GenericTarget.objects.filter(id=id).update(is_enabled=final_action)

            elif target_type == 'kb':
                KeybaseTarget.objects.filter(id=id).update(is_enabled=final_action)

            else:
                SocialTarget.objects.filter(id=id).update(is_enabled=final_action)

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)

        response = {
            'message': 'Successfully Updated'
        }
        return Response(response)


class DetectedChanges(viewsets.ViewSet):

    authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (DjangoModelPermissions, IsAuthenticated,)

    def detected_changes(self, request):
        try:
            gtr = request.data['GTR']

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        try:

            final_response = es_object.change_detection(gtr)

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'result': final_response
        }
        return Response(response)

class file(viewsets.ViewSet):

    # authentication_classes = (authentication.TokenAuthentication,)
    # permission_classes = (DjangoModelPermissions, IsAuthenticated,)

    def case_files(self, request):
        try:
            data=Case.objects.all()
            serializing = CaseDashboardsSerializer(data, many=True)
            case_data=serializing.data
            

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'result': case_data
        }
        return Response(response)        
 
    def keybase_files(self, request):
        try:
            data=Keybase.objects.all()
            serializing = KeybaseSerializer(data, many=True)
            keybase_case=serializing.data           

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'result': keybase_case
        }
        return Response(response)        

    def portfolio_files(self, request):
        try:
            data=Individual.objects.all().values_list()
            # portfolio_serializing_individual = IndividualSerializer(data, many=True)
            # portfolio_case_individual=portfolio_serializing_individual.data
            data2=Group.objects.all().values()
            # serializing_group = GroupSerializer(data2, many=True)
            # portfolio_case_group=serializing_group.data
            data3=Event.objects.all().values()
            # serializing_event = EventSerializer(data3, many=True)
            # portfolio_case_event=serializing_event.data
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)
            
        result_list = list(chain(data, data2, data3))
        # data_all = data + data2 + data3
        # data_all.update(data2)
        # data_all.update(data3)  
        response = {
            'result': result_list
        }
        return Response(response)


class UserNewsView(viewsets.ModelViewSet):

    queryset = UserNews.objects.all()
    serializer_class = UserNewsSerializer
    authentication_classes = (authentication.TokenAuthentication,)


    def list(self, request, *args, **kwargs):
        user = request.user
        queryset = UserNews.objects.filter(user= user)
        serializer = UserNewsSerializer(queryset, many=True)        
        return Response({"result":serializer.data})


    def create(self, request, *args, **kwargs):
        data = request.data
        data["user"] = request.user.id
        news_count = UserNews.objects.filter(user=data["user"]).count()
        news_checker = UserNews.objects.filter(user=data["user"], news_name__icontains=data["news_name"]).exists()

        if news_count >= 8:
            return Response({"message":"you can add only 8 news channels"}, status=status.HTTP_204_NO_CONTENT)

        if news_checker:
            return Response({"message":" '{0}' News channels already exists".format(data["news_name"])}, status=status.HTTP_204_NO_CONTENT)

        data['news_name'] = data['news_name'].upper()
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        # start crawling
        ess_object.news_crawling(top=30, news_site=serializer.data['news_name'], channel_link=serializer.data['channel_url'])

        headers = self.get_success_headers(serializer.data)
        return Response({"message":"News added Successfully","results":serializer.data}, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message":"Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)

  