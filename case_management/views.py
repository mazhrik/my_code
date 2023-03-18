import datetime
import os
from django.core import paginator
from django.db.models import Q
from django.utils import tree
import requests
import pandas as pd
import shutil
import os
from rest_framework.pagination import PageLink
from rest_framework.renderers import JSONRenderer
from OCS_Rest.settings import FTP_LOCAL_DIRECTORY, MEDIA_SERVER_BASE_PATH
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework import status
from .serializers import *
from .serializers import EventSerializer as CaseEventSerializer
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from .models import Case
from core_management.serializers import LogSerializersversion2
from keybase_management.models import Keybase
from rest_framework.response import Response
from django.db import (IntegrityError,
                       InternalError)
from portfolio_management.views import StandardResultsSetPagination
from keybase_management.serializers import KeybaseSerializer
from portfolio_management.models import Individual, LinkedData, Event, Group
from case_management.models import Event as case_event, Investigator
from target_management.models import SocialTarget, GenericTarget, KeybaseTarget
from portfolio_management.serializers import IndividualSerializer, GroupSerializer, EventSerializer
from target_management.serializers import  Leaked_data_serializer, SocialTargetListSerializer, KeybaseTargetListSerializer, \
    GenericTargetListSerializer
from rest_framework.parsers import FileUploadParser, MultiPartParser
from rest_framework.decorators import parser_classes
from core_management.file_handler import file_upload_handler, file_upload_handler_frs
from PIL import Image
from core_management.elasticsearch_handler_v2 import ElasticsearchHandler
from case_management.report_active_users_cms import get_report_content
from django.core.exceptions import PermissionDenied
from case_management.report_classification_cms import try_
import json
from core_management.models import Log
from report_management.models import ReportsNotes
from report_management.serializers import NotesSerializer
from account_management.models import Team, Team_members
from django.core.paginator import Paginator
import math
import time
from target_management.ess_controller import EssApiController
from target_management.models import LeakedData
from django.http import Http404

app_name = 'cms'
app_name_frs = 'ocs_frs'
es_obj = ElasticsearchHandler()


def perform_upload_leaked_data(req_data,sub_folder):
    serializer_copy = req_data
    print('--------------------------')
    print(serializer_copy)
    if 'leaked_data' in serializer_copy:
        try:
            
            filename = req_data['name']
            file = req_data['leaked_data']
            target_type = req_data['target_type']
            file_size = file.size
            
            folder_name = str(req_data[sub_folder])
            file_split = str(file).split('.')
            file_ext = file_split[-1]
            directory = '{0}/{1}/{2}/'.format(FTP_LOCAL_DIRECTORY, app_name, folder_name)
            app_dir = '{0}/{1}/'.format(FTP_LOCAL_DIRECTORY, app_name)
            main_directory = directory
            extension = str(folder_name) + '.' + file_ext
            leaked_file_dir = main_directory + extension
            Gtr_Leaked_Data = LeakedData(target_type=target_type, file_name=filename, file_size=file_size)
            created = Gtr_Leaked_Data.save()
            gtr_leaked = LeakedData.objects.filter(GTR=Gtr_Leaked_Data.GTR)
            Gtr_Leaked_Data_serialized_data = Leaked_data_serializer(gtr_leaked,many=True)
            Gtr_Leaked_Data_json_rendered = JSONRenderer().render(Gtr_Leaked_Data_serialized_data.data)
            Gtr_Leaked_Data_json = json.loads(Gtr_Leaked_Data_json_rendered)[0]
            # print('------------------------------------->',Gtr_Leaked_Data_json)
            print(file_size)
            try:
                print('in try2')
                print(directory)
                os.mkdir(directory)
                
                with open(leaked_file_dir, 'wb') as f:
                    f.write(file.read())

                try:
                    print('in try',leaked_file_dir)
                    for df in pd.read_csv(leaked_file_dir,chunksize=10000):
                        for index,row in df.iterrows():
                            row = row.to_dict()
                            row.update(Gtr_Leaked_Data_json)
                            # final_dict_elastic_search={'target_data': Gtr_Leaked_Data_json,'leaked_data':dict_from_csv} # muneeb
                            es_obj.leaked_data_elastic(row,target_type)

                    # print('------------------------------>',final_dict_elastic_search)
                    shutil.rmtree(main_directory)
                    print('deleted')
                    # es_obj.leaked_data_elastic(,dict_from_csv)

                    print('get leaked data')
                   
                except Exception as e : 
                    print('------->',e)    
            except Exception as e:
                print('in exception')
                print(e)
                try:
                    os.mkdir(app_dir)
                except:
                    pass
                os.mkdir(directory)
                with open(leaked_file_dir, 'wb') as f:
                    f.write(file.read())
        except Exception as ex:
            serializer_copy.update({'leaked_data': ''})
            print(ex)
    else:
        pass
    return serializer_copy


# *******************************************************************
# ************************* Shehroz Code *************************
# *******************************************************************

    # serializer_copy = req_data
    # if 'leaked_data' in serializer_copy:
        # try:
            # file = req_data['leaked_data']
            # print(f"Filename: {file}")

            # file_name = str(file).split('.')[0]
            # print(f"File name: {file_name}")
            
            # file_ext = str(file).split('.')[-1]
            # print(f"File extension: {file_ext}")

            # print('**************************')
            # print(FTP_LOCAL_DIRECTORY, app_name)

            # directory = '{0}/{1}/'.format(FTP_LOCAL_DIRECTORY, app_name)
            # app_dir = '{0}/{1}/'.format(FTP_LOCAL_DIRECTORY, app_name)
            # main_directory = directory
            # extension = str(file_name) + '.' + file_ext
            # leaked_file_dir = main_directory + extension
            # print(leaked_file_dir)


            # from core_management.hdfs_client import HDFSClient
            # import json

            # root = 'user/ocs'


            # hdfs = HDFSClient()


            # import csv
            
            # # here here here here here here
            # # with open(leaked_file_dir, 'wb+') as destination:
            #     # print(destination)
            # for ind, chunk in enumerate(file.chunks(chunk_size=5000000)):
            #     print('iiiiiiiiiiiiiiiiiiiiiiiiiiii')
            #     # print(chunk)
            #     # print(type(chunk))
            #     print(file.size)
            #     # break
            #     data = json.dumps(chunk.decode('utf-8'))
            #     # print(data)
                
            #     reader = csv.reader(data.split('\n'), delimiter=',')
                
            #     ls = []
            #     for row in reader:
            #         data = ','.join(row)
            #         ls.append(data)

            #     data2 = pd.DataFrame(list(csv.reader(ls)))
            #     final_data = data2.to_csv()
            #     print(final_data)
            #     print(type(final_data))
            #     # destination.write(chunk)
            #     filename = f"{str(file_name)}_chunk_{str(ind)}.{file_ext}"
                
            #     hdfs.create_file(data=final_data, dir_to_store=root, file_name=filename)

# *******************************************************************
# ************************* Muneeb Old Code *************************
# *******************************************************************

            # try:
            #     print('in try2')
                
            #     with open(leaked_file_dir, 'wb') as f:
            #         f.write(file.read())
                
            #     try:
            #         in_csv = str(leaked_file_dir)
            #         number_lines = sum(1 for row in (open(in_csv,encoding='latin1')))
            #         rowsize = 5
            #         pathh = '/home/shehroz/Desktop/doc'
            #         print('----------',number_lines)
                    
            #         y = 0

            #         for i in range(0,number_lines,rowsize):
            #             df = pd.read_csv(in_csv,
            #                 header=None,
            #                 nrows = rowsize,
            #                 skiprows = i,encoding='latin1')
            #             print('y',y)
                        
            #             out_csv = file_name + '_' + str(y + 1) + '.csv'
            #             y = y + 1
                        
            #             df.to_csv(os.path.join(pathh,out_csv),
            #             index=False,
            #             header=False,
            #             mode='a',
            #             chunksize=rowsize)
                # except:
                #     pass    
        
            # except Exception:
            #     try:
            #         os.mkdir(app_dir)
            #     except:
            #         pass
            #     os.mkdir(directory)
            #     with open(leaked_file_dir, 'wb') as f:
            #         f.write(file.read())



            # url, stats, ex = file_upload_handler(dir_pick_path=pathh, folder_name=folder_name, app_name=app_name)
            # if url:
            #     http_url = '{0}/{1}/{2}/{3}'.format(MEDIA_SERVER_BASE_PATH, app_name, folder_name, extension)
            #     serializer_copy.update({'leaked_data': http_url})
            #     print(serializer_copy)
            #     print('url: ', http_url)
            # print('status: ', stats)
            # print('error', ex)        

    #     except Exception as ex:
    #         serializer_copy.update({'leaked_data': ''})
    #         print(ex)
    # else:
    #     pass
    # return serializer_copy

def perform_upload(req_data, sub_folder):
    serializer_copy = req_data
    if 'image_url' in serializer_copy:
        try:
            file = req_data['image']
            folder_name = str(req_data[sub_folder])
            file_split = str(file).split('.')
            file_ext = file_split[-1]
            directory = '{0}/{1}/{2}/'.format(FTP_LOCAL_DIRECTORY, app_name, folder_name)
            app_dir = '{0}/{1}/'.format(FTP_LOCAL_DIRECTORY, app_name)
            main_directory = directory
            extension = str(folder_name) + '.' + file_ext
            image_file_dir = main_directory + extension
            try:
                with open(image_file_dir, 'wb') as f:
                    f.write(file.read())
            except Exception:
                try:
                    os.mkdir(app_dir)
                except:
                    pass
                os.mkdir(directory)
                with open(image_file_dir, 'wb') as f:
                    f.write(file.read())

            url, stats, ex = file_upload_handler(dir_pick_path=directory, folder_name=folder_name, app_name=app_name)
            if url:
                http_url = '{0}/{1}/{2}/{3}'.format(MEDIA_SERVER_BASE_PATH, app_name, folder_name, extension)
                serializer_copy.update({'image_url': http_url})
                print(serializer_copy)
                print('url: ', http_url)
            print('status: ', stats)
            print('error', ex)
        except Exception as ex:
            serializer_copy.update({'image_url': ''})
            print(ex)
    else:
        pass
    return serializer_copy

def perform_upload_frs(req_data, sub_folder):
    serializer_copy = req_data
    if 'image_url' in serializer_copy:
        try:
            file = req_data['image']
            folder_name = str(req_data[sub_folder])
            folder_name = f"{folder_name.split('.')[0]}_{str(time.time()).split('.')[0]}.{folder_name.split('.')[1]}"
            # folder_name = "{0}_{1}_{2}".format(folder_name.split('.')[0],str(time.time()).split('.')[0],folder_name.split('.')[1])
            file_split = str(file).split('.')
            file_ext = file_split[-1]
            directory = '{0}/{1}/{2}/'.format(FTP_LOCAL_DIRECTORY, app_name_frs, folder_name)
            app_dir = '{0}/{1}/'.format(FTP_LOCAL_DIRECTORY, app_name_frs)
            main_directory = directory
            extension = str(folder_name) #+ '.' + file_ext
            image_file_dir = main_directory + extension
            try:
                with open(image_file_dir, 'wb') as f:
                    f.write(file.read())
            except Exception:
                try:
                    os.mkdir(app_dir)
                except:
                    pass
                os.mkdir(directory)
                with open(image_file_dir, 'wb') as f:
                    f.write(file.read())
         
            url, stats, ex = file_upload_handler_frs(dir_pick_path=directory, folder_name=folder_name, app_name=app_name_frs)
            if url:
                http_url = '{0}/cms/{1}/{2}'.format(MEDIA_SERVER_BASE_PATH, app_name_frs, extension)
                serializer_copy.update({'image_url': http_url})
                print(serializer_copy)
                print('url: ', http_url)
            print('status: ', stats)
            print('error', ex)
        except Exception as ex:
            serializer_copy.update({'image_url': ''})
            print(ex)
    else:
        pass
    return serializer_copy


class LeakedDataViewSet(ViewSet):
    """
    Viewset for Leaked data add, delete and list
    """
    authentication_classes = (TokenAuthentication,)
    queryset = User.objects.all()
    permission_classes = ( IsAuthenticated,)

    @action(detail=True, methods=['POST'])
    def leaked_data_upload(self,request):
        try :
            print('in try')
            perform_upload_leaked_data(request.data,'leaked_data')
        except:
            pass

        response = {
            'message':"success"
        }   
        
        return Response(response)

    @action(detail=True, methods=['POST'])
    def leaked_data(self, request):
        print('in leaked data')
    
        phone = request.data.get('phone','')
        email = request.data.get('email','')
        id = request.data.get('id','')
        # print(phone_num)
        # ess = EssApiController()
        # ess_response = ess.leaked_data_whatsapp(phone_num=phone_num)
        elastic_respone= (es_obj.leaked_data_get(index='*leaked_data',phone=phone,email=email,id=id)) 

        return Response(elastic_respone)
    
    @action(detail=True, methods=['GET'])
    def leaked_data_view(self, request, **kwargs):
        checker  = 0
        
        start_date = self.request.query_params.get("start_date")
        platforms = self.request.query_params.get("platform")
        end_date = self.request.query_params.get("end_date")
        page = self.request.query_params.get("page")
        search = self.request.query_params.get("search")

        print(platforms, start_date, end_date, page, search)

        if platforms:
            platforms = platforms.split(',')
            if checker == 0:
                query = Q(target_type__in=platforms)
                checker += 1

            
        if start_date and end_date:
            if checker == 0:
                query = Q(created_on__range=[start_date, end_date])
                checker += 1
            else:
                query.add(Q(created_on__range=[start_date, end_date]), Q.AND)

        if search:
            if checker == 0:
                query = Q(file_name__icontains=search)
                checker += 1
            else:
                query.add(Q(file_name__icontains=search), Q.AND)

        if platforms or start_date or end_date or search:
            query_set = LeakedData.objects.filter(query)
            paginator = Paginator(query_set, 6)
            query = paginator.page(int(page))
            serializer = Leaked_data_serializer(query, many=True)
        else:
            query_set = LeakedData.objects.all()
            print(query_set)
            paginator = Paginator(query_set, 6)
            query = paginator.page(int(page))
            print(query)
            serializer = Leaked_data_serializer(query, many=True)

        response = {
            'message': 'All leaked data files',
            'status': True,
            'files_count':len(query_set),
            "pages": math.ceil(len(query_set)/6),
            "current_page":int(page),
            'result': serializer.data
        }

        return Response(response)

    @action(detail=True, methods=['DELETE'])
    def leaked_data_delete(self, request, **kwargs):
        # for deleting the object
        id = kwargs.get('id')
        print('**********************')
        print(id)
        
        if id:
            try:
                leaked_data = LeakedData.objects.get(id=id)

                # delete from ElasticSearch
                es_obj.delete_document(index='*_leaked_data', gtr=leaked_data.GTR)

                # delete from db
                leaked_data.delete()            

                result = {
                    'message': 'Deleted Successfully'
                }
            except:     
                result = {
                    'message': 'Item does not exist'
                }
        else:
            result = {
                'message': 'ID not given'
            }
        print(result)
        return Response(result, status=status.HTTP_200_OK)

class CaseViewSet(ViewSet):
    """
    Viewset for Social target add, delete, update and list

    """
    authentication_classes = (TokenAuthentication,)
    queryset = User.objects.all()
    permission_classes = ( IsAuthenticated,)

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return CaseListSerializer
        return CaseListSerializerV2

    @action(detail=True, methods=['POST'])
    @parser_classes(MultiPartParser, )
    def simple_upload(self, request):
        user = request.user
        file = request.data['image']
        print(file)
        image = Image.open(file)
        # FTP.disconnect()
        image.show()
        response = {
            'message': 'No Target Found',
            'status': False,
            'result': str(request.data)
        }
        return Response(response,
                        status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['GET'])
    def list(self, request):
        auth_user = request.user.has_perm('case_management.view_case')
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        user = request.user
        # all_users = User.objects.with_perm('case_management.view_case')
        # if not request.user in all_users:
        #     response = {
        #         'message': 'User has no permission to view cases'
        #     }
        #     return Response(response)
        # raise PermissionDenied()
        if 'case_id' in request.query_params:
            case_id = str(request.query_params['case_id'])
            cases = Case.objects.filter(Q(user=user) | Q(tao_investigator=user) & Q(id=case_id)).values()
        else:
            cases = Case.objects.filter(Q(user=user) | Q(tao_investigator=user)).values()

        response = {'message': 'List all the Cases',
                    'status': True,
                    'result': cases}

        return Response(response)
        # cases = Case.objects.filter(user=user)
        # print(cases)
        # response = {
        #     'result': cases
        # }
        #
        # return Response(response)

    @action(detail=True, methods=['GET'])
    def listV1(self, request):
        auth_user = request.user.has_perm('case_management.view_case')
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        user = request.user
        check = 0
        case_state = self.request.query_params.get('case_state')
        page = self.request.query_params.get('page')
        case_title = self.request.query_params.get('case_title')
        print("user.is_superuser ",user.is_superuser)
        # query =  
        if user.is_superuser == False:
     
            query = Q(user=user)
            query.add(Q(share_resource__contains=[user.id]), Q.OR)
            check = 1

        tmo_checker = 0
        if user.groups.filter(name='TMO').exists():
            team = Team.objects.filter(team_leader=user.id).first()
            team_member = Team_members.objects.filter(team = team)
            tmo_user = []
            tmo_checker = 1
            for each_user in team_member:
                tmo_user.append(each_user.user)
                tmo_checker = tmo_checker + 1
            tmo_user.append(user)
            
        if tmo_checker !=  0:
            query.add(Q(tao_investigator__in=tmo_user), Q.OR)
        else:
            if check == 0 and user.is_superuser == False:
                query = Q(tao_investigator=user)
                check = 1
            elif user.is_superuser == False :
                query.add(Q(tao_investigator=user), Q.OR)
        # if user.is_superuser:
        #     if case_state or case_title:
        #         if case_state:
        #             if check == 0:
        #                 query = Q(case_state=case_state)
        #                 check = 1
        #             else:
        #                 query.add(Q(case_state=case_state), Q.AND)

        #         if case_title:
        #             if check == 0:
        #                 query = Q(case_title__icontains=case_title)
        #                 check = 1
        #             else:
        #                 query.add(Q(case_title__icontains=case_title), Q.AND)

        #         cases = Case.objects.filter(query)
        #         cases_count = Case.objects.filter(query).count()
        #     else:
        #         cases = Case.objects.all()
        #         cases_count = Case.objects.all().count()

        # else:

        #     # query = Q(user=user)
        #     # query.add(Q(tao_investigator=user), Q.OR)

        #     if case_state:
        #         query.add(Q(case_state=case_state), Q.AND)

        #     if case_title:
        #         query.add(Q(case_title__icontains=case_title), Q.AND)

        if case_state:
            if check == 0:
                query = Q(case_state=case_state)
            else:
                query.add(Q(case_state=case_state), Q.AND)
                check = 1

        if case_title:
            if check == 0:
                query = Q(case_title__icontains=case_title)
            else:
                query.add(Q(case_title__icontains=case_title), Q.AND)

        if query:
            cases = Case.objects.filter(query)
            cases_count = Case.objects.filter(query).count()
        else:
            cases = Case.objects.all()
            cases_count = Case.objects.all().count()

        paginator = Paginator(cases, 6)
        cases = paginator.page(int(page))


        result = CaseListSerializerV2(cases, many=True)


        response = {'message': 'List all the Targets',
                        'status': True,
                        'cases_count':cases_count,
                        "pages": math.ceil(cases_count/6),
                        "current_page":int(page),
                        'result': result.data,
                        }

        return Response(response)

    def case_detail(self, request, *args, **kwargs):
        id = kwargs['id']
        obj = Case.objects.filter(id=id)
        ser = CaseListSerializer(obj, many=True)
        return Response(ser.data)

    @action(detail=True, methods=['GET'])
    def details(self, request,**kwargs):
        try:
            data = {}
            id=kwargs['id']
            contrib=Case.objects.filter(id=id)[0]
            latest_date_list=[]
            # if contrib.case_id==False:
            #     response = {
            #     'message': " case id  not found"
            # }
            username=contrib.user_id
            generated_report=Log.objects.filter(request_url='/v1/report/get/notes/')
            generated_report=LogSerializersversion2(generated_report,many=True)
            generated_report_json_data=JSONRenderer().render(generated_report.data)
            generated_reportjson_data = json.loads(generated_report_json_data)

            report_note=ReportsNotes.objects.filter(report_id=id)
            report_note_list=[]
            for each in report_note:
                report_note_dict={}
                report_note_dict['username']=each.username
                report_note_dict['note']=each.note
                report_note_dict['date']=each.date
                report_note_list.append(report_note_dict)
            data['note_contributors']=report_note_list    
            for each_date in generated_reportjson_data:
                try:
                    if each_date['request_data']['type']=='case' and  each_date['request_data']['report_id']==id:
                        date_latest=each_date['request_time']
                        latest_date_list.append(date_latest)
                except Exception as e:
                    # print(e)    
                    pass
            for each_data in generated_reportjson_data:
                try:
                    if each_data['request_data']['type']=='case' and  each_data['request_data']['report_id']==id and each_data['request_time']==max(latest_date_list):
                            report_username=User.objects.filter(id=each_data['request_username']).first()     
                            data['report_generated_by']=report_username.username
                            data['report_generated_on']=each_data['request_time']
                            # print('report_--------------------->genreated')                      
                    else:
                        pass
                except Exception as e:
                    # print(e)
                    pass
                          
                        
            user_name=User.objects.filter(id=username).first()
            data['case_description'] = contrib.case_description
            data['case_updated_on']=contrib.updated_on 
            # data['case_note']=case_notes.note
            data['case_created_on'] = contrib.created_on
            data['case_marked_by']= user_name.username
            data['case_id']=contrib.id
            obj = Case.objects.filter(id=data['case_id'])
            serilize_data = CaseListSerializer(obj, many=True)
            # serializing=CaseListSerializerV2(contrib[0])
            json_data=JSONRenderer().render(serilize_data.data)
            json1_data = json.loads(json_data)
            # print(len(json1_data[0]['linked_data'][1:]))
            if len(json1_data[0]['linked_data'])>0:
                x=(json1_data[0]['linked_data'])
                target_gtr_list=[]
                for a in x: 
                    try:
                        get_gtr=a['GTR']
                        target_gtr_list.append(get_gtr)
                    except:
                        pass     
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response, status=status.HTTP_404_NOT_FOUND)
            
        if len(json1_data[0]['linked_data'])>0:
            x=(json1_data[0]['linked_data'])
            y=[]
            z=[]
            for a in x:
                try:
                    user=a['user']
                    y.append(user)
                except:
                    pass    
            for a in y:
                dict_target={}
                id=a
                k=User.objects.filter(id=id).first()
                username=k.username
                date_joined=k.date_joined
                dict_target['username']=username
                dict_target['date_joined']=date_joined
                z.append(dict_target)
            
            data['target_marked_by']=z    
            json_data_operation = Log.objects.filter(request_url__icontains="/v1/target/set/response/")
            operation_by = []
            for each_data in json_data_operation:
                try:
                    # gtr_access =each_data['request_data']['GTR']
                    gtr_access =each_data.request_data['GTR']
                    length=len(target_gtr_list)
                    x=0
                    while x!=length:
                        operation_by_dic = {}
                        if gtr_access==target_gtr_list[x]:
                            print(gtr_access)
                            operation_by_dic['user']=each_data.request_username.username
                            operation_by_dic['time']=each_data.request_time
                            operation_by.append(operation_by_dic) 
                            # operation_gtr_list.append(gtr_access)
                        x=x+1    
                except Exception as e:
                    # print(e)
                    pass
            unique_contributors=[] 
            for i in z :
                unique_contributors.append(i['username'])
            print(unique_contributors)    
            total_unique_contributors=set(unique_contributors)
            unique_contributors2=[] 
            for each in operation_by :
                unique_contributors2.append(each['user'])
            print(unique_contributors2)    
            total_unique_contributors2=set(unique_contributors2)
            length_of_contributors=len(total_unique_contributors)+len(total_unique_contributors2)
            data['total_contributors']=length_of_contributors
            data['operations_by'] = operation_by
            response = {
                'result':data
                }
            return Response(response)
        else:
            response = {
                'result': data,
                'alert':"no targets found"
                }
            return Response(response)    
   

    @action(detail=True, methods=['POST'])
    def create(self, request):
        auth_user = request.user.has_perm('case_management.add_case')
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        target_detail = request.data.copy()

        if Case.objects.filter(case_title=target_detail['case_title']).exists():
            response = {
                        'message': 'Case Title should be unique!',
                        'status': True,
                        'result': []
                    }
            
            return Response(response, status=status.HTTP_200_OK)

        try:
            if target_detail['tao_investigator']:
                tao_investigator_user_id =target_detail['tao_investigator']
                tao_investigator_user = User.objects.get(id=tao_investigator_user_id)
                target_detail['tao_investigator'] = tao_investigator_user
            else:
                pass
        except:
            pass        
        expire_date = datetime.datetime.fromtimestamp(
            float(target_detail['expire_on']) / 1000) + datetime.timedelta(hours=11)
        target_detail.update({'expire_on': expire_date})
        incident_datetime = datetime.datetime.fromtimestamp(
            float(target_detail['incident_datetime']) / 1000) + datetime.timedelta(hours=11)
        target_detail.update({'incident_datetime': incident_datetime})
        # apply_ai = set(target_detail['apply_ai'])
        # print('afterset', apply_ai)
        # target_detail.update({'apply_ai': apply_ai})
        if request.data is not None:
            try:
                case = Case()
                for attr, value in target_detail.items():
                    setattr(case, attr, value)
                    print('Attribute', attr)
                    print('Value', value)

                if Case.get_case_count():

                    created = case.save()
                    if created:
                        result = self.get_serializer_class()(
                            instance=case,
                            many=False).data
                    else:
                        result = "Target not Marked"
                    print(result)
                    response = {
                        'message': 'Case Created Successfully',
                        'status': True,
                        'case_details': request.data,
                        'result': result
                    }
                    return Response(response, status=status.HTTP_200_OK)
                else:
                    response = {
                        'message': 'Case Limit Exceed for today'
                    }
                    return Response(response)
            except Exception as e:
                response = {
                    'message': 'Target url Already found:  {0}'.format(e),
                    'status': False,
                    'result': None
                }
                return Response(response, status=status.HTTP_204_NO_CONTENT)

            except Exception as E:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': str(E)
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

        else:
            response = {
                'message': 'Please provide the data',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True,
            methods=['POST'])
    def update(self, request):
        auth_user = request.user.has_perm('case_management.change_case')
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        # all_users = User.objects.with_perm('case_management.change_case')
        # if not request.user in all_users:
        #     response = {
        #         'message': 'User has no permission to update cases'
        #     }
        #     print(response)
        #     return Response(response)
        if 'id' in request.data:
            case_id_params = str(request.data['id'])
        else:
            case_id_params = None
        update_detail = request.data.copy()
        if 'expire_on' in request.data:
            expire_date = datetime.datetime.fromtimestamp(
                float(update_detail['expire_on']) / 1000) + datetime.timedelta(hours=11)
            update_detail.update({'expire_on': expire_date})
        if 'incident_datetime' in request.data:
            incident_datetime = datetime.datetime.fromtimestamp(
                float(update_detail['incident_datetime']) / 1000) + datetime.timedelta(hours=11)
            update_detail.update({'incident_datetime': incident_datetime})
        if 'tao_investigator' in request.data:
            update_detail.update({'tao_investigator': User.objects.filter(id = request.data['tao_investigator'] ).first()})
        if all(v is not None for v in [case_id_params, update_detail]):
            if Case.objects.filter(id=case_id_params):
                target = Case.objects.filter(id=case_id_params).first()
            else:
                target = None
                print('not')
            if target is None:
                response = {
                    'message': 'Case object not found for selected target',
                    'status': False,
                    'result': None
                }
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
                    'message': 'Case Updated Successfully',
                    'status': True,
                    'result': result
                }
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Target url Already found',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params or data missing',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["GET"])
    def get_tao_investigator(self, request):
        # first check if the user is TAO or not 
        #list all the TAO users second check if its a TAO that user can be assigned to the tao_investigator
        try:
            user = request.user 
            tao_list = []
            list_of_tmo = []
            tmo=[]
            if user.is_superuser:
                
                teams = Team.objects.all()
                
                for each_team in teams:
                    leader = {}
                    if each_team.team_leader.groups.filter(name='TMO').exists():
                        member_check = Team_members.objects.filter(team = each_team)
                        list_of_tao = []
                        for member in member_check:
                            
                            if member.user.groups.filter(name='TAO').exists():
                                tao_dic = {}
                                # tao_dic["TMO_leader"] = each_team.team_leader.username
                                tao_dic['user'] = member.user.username
                                tao_dic['id'] = member.user.id
                                list_of_tao.append(tao_dic)
                        leader["TMO_leader"] = each_team.team_leader.username
                        leader["TMO_members"] = list_of_tao
                        tmo.append(each_team.team_leader.username)
                        list_of_tmo.append(each_team.team_leader.username)
                        tao_list.append(leader)


            elif user.groups.filter(name='TMO').exists():
                leader = {}
                lead_check = Team.objects.filter(team_leader=user.id).first()
                member_check = Team_members.objects.filter(team=lead_check)
                list_of_tao = []
                for member in member_check:
                    
                    if member.user.groups.filter(name='TAO').exists():
                        tao_dic = {}
                        # tao_dic["TMO_leader"] = each_team.team_leader.username
                        tao_dic['user'] = member.user.username
                        tao_dic['id'] = member.user.id
                        list_of_tao.append(tao_dic)
                tmo.append(lead_check.team_leader.username)
                leader["TMO_leader"] = lead_check.team_leader.username
                leader["TMO_members"] = list_of_tao

                list_of_tmo.append(lead_check.team_leader.username)
                tao_list.append(leader)
        # for member in member_check:
                #     if member.user.groups.filter(name='TAO').exists():
                #         tao_dic = {}
                #         tao_dic['user'] = member.user.username
                #         tao_dic['id'] = member.user.id
                #         tao_list.append(tao_dic)
                # list_of_tmo.append(lead_check.team_leader.username)
            
            response = {
            'message': 'sorry you are not TMO',
            'status': False,
            'result': tao_list,
            'TMO':tmo
            }
            return Response(response)
                
        except Exception as e:
            return Response(str(e))



    @action(detail=True, methods=['GET'])
    def destroy(self, request):
        all_users = User.objects.with_perm('case_management.delete_case')
        if not request.user in all_users:
            response = {
                'message': 'User has no permission to delete case'
            }
            return Response(response)
        if 'target_id' in request.query_params:
            target_id = str(request.query_params['target_id'])
        else:
            target_id = None
        print(target_id)
        if all(v is not None for v in [target_id]):
            if Case.objects.filter(id=target_id):
                target = Case.objects.filter(id=target_id).first()
            else:
                target = None
            if target is None:
                response = {
                    'message':
                        'Target object not found for selected target id',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_204_NO_CONTENT)

            try:
                target.delete()
                response = {
                    'message': 'Target Deleted Successfully',
                    'status': True,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_200_OK)

            except Exception as e:
                response = {
                    'message': str(e),
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params Missing',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def attach_person(self, request):
        user = request.user
        print("Request By User: ", user)
        data_dict = request.data.copy()
        keys = [*data_dict]
        if set(keys) == {'info_id', 'case_id', 'operation'}:
            info_id, case_id, operation = data_dict['info_id'], data_dict['case_id'], data_dict['operation']
            try:
                if Case.objects.filter(id=case_id):
                    case = Case.objects.filter(id=case_id).first()
                    serializer = self.get_serializer_class()
                else:
                    case, serializer = None, None
                if case is None:
                    response = {
                        'message': 'No Case or Investigator Found',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                info = Person.objects.filter(id=info_id).first()
                if operation == 'attach':
                    updated = case.people.add(info)
                else:
                    updated = case.people.remove(info)
                if updated:
                    result = serializer(
                        instance=case,
                        many=False).data
                else:
                    result = None
                response = {
                    'message': 'Person Attached Successfully',
                    'status': True,
                    'result': result
                }
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Duplication Error',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params or data missing',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=['POST'])
    def attach_investigator(self, request):
        user = request.user
        print("Request By User: ", user)
        data_dict = request.data.copy()
        print(request.data)
        keys = [*data_dict]
        if set(keys) == {'info_id', 'case_id', 'operation'}:
            info_id, case_id, operation = data_dict['info_id'], data_dict['case_id'], data_dict['operation']
            try:
                if Case.objects.filter(id=case_id):
                    case = Case.objects.filter(id=case_id).first()
                    serializer = self.get_serializer_class()
                else:
                    case, serializer = None, None
                if case is None:
                    response = {
                        'message': 'No Case or Investigator Found',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                info = Investigator.objects.filter(id=info_id).first()
                if operation == 'attach':
                    updated = case.investigators.add(info)
                else:
                    updated = case.investigators.remove(info)
                if updated:
                    result = serializer(
                        instance=case,
                        many=False).data
                else:
                    result = None
                response = {
                    'message': 'Investigator Attached Successfully',
                    'status': True,
                    'result': result
                }
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Duplication Error',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params or data missing',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_400_BAD_REQUEST)

    def deattach_investigator(self, request):
        case_id = request.data['case_id']
        info_id = request.data['info_id']

        try:
            case_obj = Case.objects.filter(id=case_id).first()
            investigator_obj = Investigator.objects.filter(id=info_id).first()
            case_obj.investigators.remove(investigator_obj)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'message': 'Investigator Removed Successfully'
        }
        return Response(response, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def attach_location(self, request):
        user = request.user
        print("Request By User: ", user)
        data_dict = request.data.copy()
        print('data_dict', data_dict)
        keys = [*data_dict]
        if set(keys) == {'info_id', 'case_id', 'operation'}:
            info_id, case_id, operation = data_dict['info_id'], data_dict['case_id'], data_dict['operation']
            try:
                if Case.objects.filter(id=case_id):
                    case = Case.objects.filter(id=case_id).first()
                    serializer = self.get_serializer_class()
                else:
                    case, serializer = None, None
                if case is None:
                    response = {
                        'message': 'No Case or Investigator Found',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                info = Location.objects.filter(id=info_id).first()
                if operation == 'attach':
                    updated = case.locations.add(info)
                else:
                    updated = case.locations.remove(info)
                if updated:
                    result = serializer(
                        instance=case,
                        many=False).data
                else:
                    result = None
                response = {
                    'message': 'Location Attached Successfully',
                    'status': True,
                    'result': result
                }
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Duplication Error',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params or data missing',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['POST'])
    def attach_media(self, request):
        user = request.user
        print("Request By User: ", user)
        print("---------------------------------------", request.data)
        data_dict = request.data.copy()
        keys = [*data_dict]
        if set(keys) == {'info_id', 'case_id', 'operation'}:
            info_id, case_id, operation = data_dict['info_id'], data_dict['case_id'], data_dict['operation']
            try:
                if Case.objects.filter(id=case_id):
                    case = Case.objects.filter(id=case_id).first()
                    serializer = self.get_serializer_class()
                else:
                    case, serializer = None, None
                if case is None:
                    response = {
                        'message': 'No Case or Investigator Found',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                info = Media.objects.filter(id=info_id).first()
                if operation == 'attach':
                    updated = case.media.add(info)
                else:
                    updated = case.media.remove(info)
                if updated:
                    result = serializer(
                        instance=case,
                        many=False).data
                else:
                    result = None
                response = {
                    'message': 'Media Attached Successfully',
                    'status': True,
                    'result': result
                }
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Duplication Error',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params or data missing',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def attach_evidence(self, request):
        user = request.user
        print("Request By User: ", user)
        data_dict = request.data.copy()
        keys = [*data_dict]
        if set(keys) == {'info_id', 'case_id', 'operation'}:
            info_id, case_id, operation = data_dict['info_id'], data_dict['case_id'], data_dict['operation']
            try:
                if Case.objects.filter(id=case_id):
                    case = Case.objects.filter(id=case_id).first()
                    serializer = self.get_serializer_class()
                else:
                    case, serializer = None, None
                if case is None:
                    response = {
                        'message': 'No Case or Investigator Found',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                info = Evidence.objects.filter(id=info_id).first()
                if operation == 'attach':
                    updated = case.evidences.add(info)
                else:
                    updated = case.evidences.remove(info)
                if updated:
                    result = serializer(
                        instance=case,
                        many=False).data
                else:
                    result = None
                response = {
                    'message': 'Evidence Attached Successfully',
                    'status': True,
                    'result': result
                }
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Duplication Error',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params or data missing',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def attach_event(self, request):
        user = request.user
        print(request.data)
        print("Request By User: ", user)
        data_dict = request.data.copy()
        keys = [*data_dict]
        if set(keys) == {'info_id', 'case_id', 'operation'}:
            info_id, case_id, operation = data_dict['info_id'], data_dict['case_id'], data_dict['operation']
            try:
                if Case.objects.filter(id=case_id):
                    case = Case.objects.filter(id=case_id).first()
                    serializer = self.get_serializer_class()
                else:
                    case, serializer = None, None
                if case is None:
                    response = {
                        'message': 'No Case or Investigator Found',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                info = case_event.objects.filter(id=info_id).first()
                if operation == 'attach':

                    updated = case.case_event.add(info)

                else:
                    updated = case.case_event.remove(info)
                if updated:
                    result = serializer(
                        instance=case,
                        many=False).data
                else:
                    result = None
                response = {
                    'message': 'Event Attached Successfully',
                    'status': True,
                    'result': result
                }
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Duplication Error',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params or data missing',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['POST'])
    def link_data(self, request):
        auth_user = request.user.has_perm('case_management.add_case')
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        user = request.user
        print("Request By User: ", user)
        data_dict = request.data.copy()
        print("--------------", request.data)
        keys = [*data_dict]
        if set(keys) == {'case_id', 'data_id', 'data_type', 'operation'}:
            case_id, data_id, data_type, operation = data_dict['case_id'], data_dict['data_id'], \
                                                     data_dict['data_type'], \
                                                     data_dict['operation']
            try:
                if data_type == 'individual':
                    if Individual.objects.filter(id=data_id):
                        portfolio = Individual.objects.filter(id=data_id).first()
                        serializer = IndividualSerializer
                    else:
                        portfolio, serializer = None, None
                elif data_type == 'group':
                    if Group.objects.filter(id=data_id):
                        portfolio = Group.objects.filter(id=data_id).first()
                        serializer = GroupSerializer
                    else:
                        portfolio, serializer = None, None
                elif data_type == 'event':
                    if Event.objects.filter(id=data_id):
                        portfolio = Event.objects.filter(id=data_id).first()
                        serializer = EventSerializer
                    else:
                        portfolio, serializer = None, None
                elif data_type == 'social':
                    if SocialTarget.objects.filter(id=data_id):
                        portfolio = SocialTarget.objects.filter(id=data_id).first()
                        serializer = SocialTargetListSerializer
                    else:
                        portfolio, serializer = None, None
                elif data_type == 'keybase':
                    if KeybaseTarget.objects.filter(id=data_id):
                        portfolio = KeybaseTarget.objects.filter(id=data_id).first()
                        serializer = KeybaseTargetListSerializer
                    else:
                        portfolio, serializer = None, None
                elif data_type == 'generic':
                    if GenericTarget.objects.filter(id=data_id):
                        portfolio = GenericTarget.objects.filter(id=data_id).first()
                        serializer = GenericTargetListSerializer
                    else:
                        portfolio, serializer = None, None
                elif data_type == 'link_data':
                    if LinkedData.objects.filter(id=data_id):
                        portfolio = LinkedData.objects.filter(id=data_id).first()
                        serializer = GenericTargetListSerializer

                elif data_type == 'keybase_data':
                    if Keybase.objects.filter(id=data_id):
                        portfolio = Keybase.objects.filter(id=data_id).first()
                        serializer = KeybaseSerializer

                if portfolio is None:
                    response = {
                        'message': 'Target object not found for selected target',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                if Case.objects.filter(id=case_id):
                    case = Case.objects.filter(id=case_id).first()
                else:
                    case = None
                if operation == 'attach' and case:
                    updated = case.linked_data.add(portfolio)
                else:
                    updated = case.linked_data.remove(portfolio)
                if updated:
                    result = serializer(
                        instance=case,
                        many=False).data
                else:
                    result = None
                response = {
                    'message': 'Target Updated Successfully',
                    'status': True,
                    'result': result
                }
                return Response(response,
                                status=status.HTTP_200_OK)
            except Exception as e:
                print("exception as ",e)
                response = {
                    'message': 'Target url Already found',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)

            except InternalError:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_409_CONFLICT)
        else:
            response = {
                'message': 'Params or data missing',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_404_NOT_FOUND)

    def case_filter(self, request):
        try:

            start_date = request.data['start_date']
            end_date = request.data['end_date']
            if request.user.is_superuser:
                case = Case.objects.filter(created_on__range=[start_date, end_date])
            elif request.user.groups.filter(~Q(name="TMO")).exists() == True:
                case = Case.objects.filter(created_by=request.user).filter(created_on__range=[start_date, end_date])
                
            elif request.user.groups.filter(name='TMO').exists() == True:
                tmo = request.user
                team = Team.objects.filter(team_leader=tmo).first()
                team_memberes = Team_members.objects.filter(team=team)
                print(team_memberes)
                list_of_user = []
                for each_team_member in team_memberes:
                    list_of_user.append(each_team_member.user)
                list_of_user.append(tmo)
                case = Case.objects.filter(created_by__in=list_of_user).filter(created_on__range=[start_date, end_date])

            serialized_data = CaseDashboardsSerializer(case, many=True)

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'result': serialized_data.data
        }
        return Response(response)


class LocationViewSet(ModelViewSet):

    authentication_classes = (TokenAuthentication,)
    queryset = Location.objects.all().order_by('id')
    pagination_class = StandardResultsSetPagination
    # permission_classes = (DjangoModelPermissions, IsAuthenticated,)

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return LocationListSerializer
        return LocationListSerializer


class InvestigatorViewSet(ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    queryset = Investigator.objects.all().order_by('id')
    permission_classes = (DjangoModelPermissions, IsAuthenticated,)
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return InvestigatorListSerializer
        return InvestigatorListSerializer

    def create(self, request, *args, **kwargs):
        auth_user = request.user.has_perm('case_management.add_investigator')
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        # status_code = status
        # print(status_code)
        # all_users = User.objects.with_perm('case_management.add_investigator')
        # if not request.user in all_users:
        #     response = {
        #         'message': 'User has no permission to Create Investigator'
        #     }
        #     print(response)
        #     return Response(response, status=status.HTTP_403_FORBIDDEN)
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            data = perform_upload(request.data, 'employee_id')
            serializer = self.get_serializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            headers = self.get_success_headers(serializer.data)
            response = {
                'message': 'Created Successfully',
                'status': True,
                'result': serializer.data
            }
            return Response(response, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

    def update(self, request, *args, **kwargs):
        # all_users = User.objects.with_perm('case_management.change_investigator')
        # if not request.user in all_users:
        #     response = {
        #         'message': 'User has no permission to Update Investigator'
        #     }
        #     return Response(response)
        id = request.data['id']
        data = perform_upload(request.data, 'employee_id')
        first_name = data['first_name']
        last_name = data['last_name']
        image_url = data['image_url']
        employee_id = data['employee_id']
        phone = data['phone']
        cnic = data['cnic']
        email = data['email']
        investigator_type = data['investigator_type']
        print("-------------------IMAGE URL-------------------", image_url)
        if id:
            try:
                investigator = Investigator.objects.filter(id=id).values()
                investigator.update(first_name=first_name, last_name=last_name, image_url=image_url,
                                    employee_id=employee_id, phone=phone, cnic=cnic, email=email,
                                    investigator_type=investigator_type)

            except Exception as error:
                response = {
                    'message': str(error)
                }
                return Response(response)

            response = {
                'message': 'Successfully updated'
            }
            return Response(response)


class PersonViewSet(ModelViewSet):

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return PersonListSerializer
        return PersonListSerializer

    authentication_classes = (TokenAuthentication,)
    queryset = Person.objects.all()
    permission_classes = (DjangoModelPermissions, IsAuthenticated,)
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        # all_users = User.objects.with_perm('case_management.add_person')
        # if not request.user in all_users:
        #     response = {
        #         'message': 'User has no permission to Create Person'
        #     }
        #     print(response)
        #     return Response(response)
        try:
            person = Person(first_name=request.data.get('first_name', ''),
                            last_name=request.data.get('last_name', ''),
                            description=request.data.get('description', ''),
                            gender=request.data.get('gender', ''),
                            phone=request.data.get('phone', ''),
                            cnic=request.data.get('cnic', ''),
                            category=request.data.get('category'),
                            email=request.data.get('email', ''),
                            picture=request.data.get('picture', ''),
                            language=request.data.get('language', ''),
                            accent=request.data.get('accent', ''),
                            can_read=request.data.get('can_read', False),
                            can_write=request.data.get('can_write', False),
                            can_speak=request.data.get('can_speak', False),
                            fluency=request.data.get('fluency', ''),
                            )
            person.save()
        except Exception as error:
            print("------------------", error, "----------------------")
            return Response({"Failed": "Unsuccessful"})
        return Response({"id": person.id})


class EvidenceViewSet(ModelViewSet):

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return EvidenceListSerializer
        return EvidenceListSerializer

    authentication_classes = (TokenAuthentication,)
    queryset = Evidence.objects.all().order_by('id')
    permission_classes = (DjangoModelPermissions, IsAuthenticated,)


class MediaViewSet(ModelViewSet):

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return MediaListSerializer
        return MediaListSerializer

    authentication_classes = (TokenAuthentication,)
    queryset = Media.objects.all().order_by('id')
    permission_classes = (DjangoModelPermissions, IsAuthenticated,)
    pagination_class = StandardResultsSetPagination

    def create(self, request, *args, **kwargs):
        # all_users = User.objects.with_perm('case_management.add_media')
        # if not request.user in all_users:
        #     response = {
        #         'message': 'User has no permission to Add Media'
        #     }
        #     print(response)
        #     return Response(response)
        print("------------------", request.data)
        data = request.data.copy()
        data["media_url"] = ""
        data["image_url"] = ""
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        test = perform_upload(data, 'image')
        # print("data---------------------------------->",test)
        # data.update({'media_url': data['image_url']})
        # print("data['image_url']  -------------< ",test["image_url"])
        data["media_url"] = test['image_url']




        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        # serializer.save()
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = {
            'message': 'Created Successfully',
            'status': True,
            'result': serializer.data
        }
        return Response(response, status=status.HTTP_200_OK, headers=headers)


class UserViewSet(ModelViewSet):

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return CaseInvestigationMapSerializer
        return CaseInvestigationMapSerializer

    authentication_classes = (TokenAuthentication,)
    queryset = User.objects.all().order_by('id')
    permission_classes = (DjangoModelPermissions, IsAuthenticated,)
    pagination_class = StandardResultsSetPagination


class CaseInvestigationMapViewSet(ModelViewSet):
    """
    Case Investigation Map
    """
    authentication_classes = (TokenAuthentication,)
    queryset = CaseInvestigationMap.objects.all().order_by('id')
    permission_classes = (DjangoModelPermissions, IsAuthenticated,)
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return CaseInvestigationMapSerializer
        return CaseInvestigationMapSerializer

    def create(self, request, *args, **kwargs):
        # all_users = User.objects.with_perm('case_management.add_caseinvestigationmap')
        # if not request.user in all_users:
        #     response = {
        #         'message': 'User has no permission to Case Investigator Map'
        #     }
        #     print(response)
        #     return Response(response)
        try:
            data = request.data
            print(data)
            cib_location = None
            case = None
            serializer_copy = data.copy()
            if 'case_id' in serializer_copy:
                case_id = serializer_copy['case_id']
                print(case_id)
                if Case.objects.filter(id=case_id):
                    case = Case.objects.get(id=case_id)
                    print(case)
                    specific_location = case.locations.all()[0]
                    specific_location_id = specific_location.id
                    cib_location = Location.objects.get(id=specific_location_id)
                    print('id', specific_location_id)
                else:
                    specific_location_id = None
                serializer_copy.update({'location': specific_location_id})
                del serializer_copy['case_id']
                print('ada', serializer_copy)
            else:
                response = {
                    'message': 'Params or data missing',
                    'status': True,
                    'result': None
                }
                return Response(response, status=status.HTTP_204_NO_CONTENT)

            serializer = self.get_serializer(data=serializer_copy)
            serializer.is_valid(raise_exception=True)
            cib_object = serializer.save()
            headers = self.get_success_headers(serializer.data)
            result = serializer.data
            if case:
                case.case_map.add(cib_object)
            if cib_location:
                result.update({'cib_location': LocationListSerializer(instance=cib_location, many=False).data})
            else:
                pass
            response = {
                'message': 'Created CIB Successfully',
                'status': True,
                'result': result
            }
            return Response(response, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as ex:
            response = {
                'message': 'Error while creating',
                'status': True,
                'result': str(ex)
            }
            print(ex)
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


class EventViewSet(ViewSet):
    """
    Event View Sets
    """

    authentication_classes = (TokenAuthentication,)
    queryset = Event.objects.all().order_by('id')
    permission_classes = (DjangoModelPermissions, IsAuthenticated,)

    # pagination_class = StandardResultsSetPagination
    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return CaseEventSerializer
        return CaseEventSerializer

    def create_event(self, request):
        # all_users = User.objects.with_perm('case_management.add_event')
        # if not request.user in all_users:
        #     response = {
        #         'message': 'User has no permission to create Event'
        #     }
        #     print(response)
        #     return Response(response)
        event_name = request.data['name']
        task = request.data['task']
        category = request.data['category']
        start_date = request.data['start_date']
        end_date = request.data['end_date']
        description = request.data['description']
        changed_start_date = datetime.datetime.fromtimestamp(float(start_date) / 1000)
        changed_end_date = datetime.datetime.fromtimestamp(float(end_date) / 1000)

        try:
            event_object = case_event(name=event_name, category=category, description=description,
                                      task=task, start_date=changed_start_date, end_date=changed_end_date)
            event_object.save()
            result = self.get_serializer_class()(
                instance=event_object,
                many=False).data
            response = {
                'message': 'Created Successfully',
                'result': result
            }
            return Response(response, status=status.HTTP_200_OK)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

    def update_event(self, request):
        # all_users = User.objects.with_perm('case_management.change_event')
        # if not request.user in all_users:
        #     response = {
        #         'message': 'User has no permission to Update Event'
        #     }
        #     print(response)
        #     return Response(response)
        print('-------------UPDATE----------------', request.data)
        try:
            id = request.data['id']
            event_name = request.data['name']
            task = request.data['task']
            start_date = request.data['start_date']
            end_date = request.data['end_date']
            description = request.data['description']
            changed_start_date = datetime.datetime.fromtimestamp(float(start_date) / 1000)
            changed_end_date = datetime.datetime.fromtimestamp(float(end_date) / 1000)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)
        try:

            event_obj = case_event.objects.filter(id=id).values()
            event_obj.update(name=event_name, task=task, start_date=changed_start_date, end_date=changed_end_date,
                             description=description)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'message': 'Successfully Updated'
        }
        return Response(response)

    def delete_event(self,request, *args, **kwargs):
        # all_users = User.objects.with_perm('case_management.delete_event')
        # if not request.user in all_users:
        #     response = {
        #         'message': 'User has no permission to Delete Event'
        #     }
        #     print(response)
        #     return Response(response)
        try:
            id = kwargs['id']
            event_obj = case_event.objects.filter(id=id)

            event_obj.delete()

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'message': 'Deleted Successfully'
        }
        return Response(response, status=status.HTTP_200_OK)


class ShapeViewSet(ModelViewSet):
    """
    Shape View Set
    """

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return ShapesSerializer
        return ShapesSerializer

    authentication_classes = (TokenAuthentication,)
    queryset = Shape.objects.all()
    permission_classes = (DjangoModelPermissions, IsAuthenticated,)
    pagination_class = StandardResultsSetPagination


class CaseReportGeneration(ViewSet):
    authentication_classes = (TokenAuthentication,)

    def generate_commentors_classification_report_cms(self, request):
        platform = 'instagram'
        fianl = {}
        category = request.data['category']
        case_id = request.data['case_id']
        platform_gtr = es_obj.get_GTR_per_platform('instagram')
        if platform_gtr is not None:
            to_be_saved = try_(es_obj.get_gtrs_in_case(platform_gtr, case_id), category, 'instagram')
            fianl['instagram'] = to_be_saved
        platform_gtr = es_obj.get_GTR_per_platform('facebook')
        if platform_gtr is not None:
            to_be_saved = try_(es_obj.get_gtrs_in_case(platform_gtr, case_id), category, 'facebook')
            fianl['facebook'] = to_be_saved
        platform_gtr = es_obj.get_GTR_per_platform('twitter')
        if platform_gtr is not None:
            to_be_saved = try_(es_obj.get_gtrs_in_case(platform_gtr, case_id), category, 'twitter')
            fianl['twitter'] = to_be_saved
        platform_gtr = es_obj.get_GTR_per_platform('linkedin')
        if platform_gtr is not None:
            to_be_saved = try_(es_obj.get_gtrs_in_case(platform_gtr, case_id), category, 'linkedin')
            fianl['linkedin'] = to_be_saved
        platform_gtr = es_obj.get_GTR_per_platform('reddit')
        if platform_gtr is not None:
            to_be_saved = try_(es_obj.get_gtrs_in_case(platform_gtr, case_id), category, 'reddit')
            fianl['reddit'] = to_be_saved
            response = {
                'result': fianl
            }
            return Response(response)
        else:
            return Response({"message": "invalid platform"})

    def generate_active_users_report(self, request):
        # platform = request.data['platform']
        final = {}

        case_id = request.data['case_id']
        platform_gtr = es_obj.get_GTR_per_platform('instagram')
        if platform_gtr is not None:
            final_list = []
            to_be_saved = get_report_content(es_obj.get_gtrs_in_case(platform_gtr, case_id))
            for d in to_be_saved:
                data = {}
                data['Category'] = d
                data['value'] = to_be_saved[d]
                final_list.append(data)
            final['instagram'] = final_list
        print(final)
        platform_gtr = es_obj.get_GTR_per_platform('twitter')
        if platform_gtr is not None:
            final_list = []
            to_be_saved = get_report_content(es_obj.get_gtrs_in_case(platform_gtr, case_id))
            for d in to_be_saved:
                data = {}
                data['Category'] = d
                data['value'] = to_be_saved[d]
                final_list.append(data)
            final['twitter'] = final_list
        platform_gtr = es_obj.get_GTR_per_platform('facebook')
        if platform_gtr is not None:
            final_list = []
            to_be_saved = get_report_content(es_obj.get_gtrs_in_case(platform_gtr, case_id))
            for d in to_be_saved:
                data = {}
                data['Category'] = d
                data['value'] = to_be_saved[d]
                final_list.append(data)
            final['facebook'] = final_list
        platform_gtr = es_obj.get_GTR_per_platform('linkedin')
        if platform_gtr is not None:
            final_list = []
            to_be_saved = get_report_content(es_obj.get_gtrs_in_case(platform_gtr, case_id))
            for d in to_be_saved:
                data = {}
                data['Category'] = d
                data['value'] = to_be_saved[d]
                final_list.append(data)
            final['linkedin'] = final_list
        platform_gtr = es_obj.get_GTR_per_platform('reddit')
        if platform_gtr is not None:
            final_list = []
            to_be_saved = get_report_content(es_obj.get_gtrs_in_case(platform_gtr, case_id))
            for d in to_be_saved:
                data = {}
                data['Category'] = d
                data['value'] = to_be_saved[d]
                final_list.append(data)
            final['reddit'] = final_list
        # print(final)
        response = {
            'result': final
        }
        return Response(response)
