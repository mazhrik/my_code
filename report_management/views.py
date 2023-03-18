import json
from portfolio_management.models import Group, Individual,Event

from django.contrib.auth.models import User
from django.shortcuts import render
import requests
from rest_framework import authentication, status, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import NotesSerializer
from .models import ReportsNotes
from rest_framework.renderers import JSONRenderer
from .serializers import NotesSerializer, BriefSerializer
from .models import ReportsNotes, Brief
from case_management.models import Case
from case_management.serializers import CaseDashboardsSerializer
from target_management.models import KeybaseTarget, SocialTarget
from keybase_management.models import Keybase
from portfolio_management.models import Event
class ReportNotesView(viewsets.ViewSet):

    authentication_classes = (TokenAuthentication,)

    def get_notes(self, request):
        auth_user = request.user.has_perm("report_management.can_download_report")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        user = request.user
        final_dict = {}
        report_type = []
        notes_by_user = []
        user_list = []

        try:
            type = request.data['type']
            report_id = request.data['report_id']

        except Exception as error:
            response = {
                'error': str(error)
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = ReportsNotes.objects.filter(type=type).filter(report_id=report_id).values()

            for r in result:
                final_dict['name'] = r['username']
                # final_dict['type'] = r['type']
                user_list.append(r['username'])
                report_type.append(r['type'])
                # notes_by_user.append(ReportsNotes.objects.filter(username=r['username']).values('note', 'date'))
                # final_dict['notes'] = ReportsNotes.objects.filter(username=r['username']).values('note', 'date')
            user_list = set(user_list)
            user_list = list(user_list)
            # report_type = set(report_type)
            # report_type = list(report_type)

            for user in user_list:
                final_dict['name'] = user

                final_dict['notes'] = ReportsNotes.objects.filter(username=user).filter(type=type).filter(
                    report_id=report_id).values('note', 'date')
                notes_by_user.append(final_dict)
                final_dict = {}

            #
            # notes.append(final_dict)
            print(final_dict)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'result': result,
            'user_list': notes_by_user,
             'current_user': str(user)
        }
        return Response(response, status=status.HTTP_200_OK)

    def add_notes(self, request):
        try:
            report_id = request.data['report_id']
            type = request.data['type']
            note = request.data['note']
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)
        print(request.data)
        try:
            ReportsNotes.objects.create(report_id=report_id, type=type, username=request.user, note=note)

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'message': 'Note added on report'
        }
        return Response(response)


    def contributors(self, request):
        auth_user = request.user.has_perm("core_management.tools_permission")
        print(auth_user)
        if auth_user == False:
            response = {
                'message': 'permission missing',
                'status': False,
                'result': None
                }
            return Response(response,status=status.HTTP_403_FORBIDDEN)
        try:
            contrib=ReportsNotes.objects.all()
            serializing=NotesSerializer(contrib,many=True)
            dson_data=JSONRenderer().render(serializing.data)
            json1_data = json.loads(dson_data)
            list_1=[]
            case_list_2=[]
            targetSummary_list_2=[]
            targetDetail_list_2=[]
            portfolio_list_2=[]
            keybase_list_2=[]
            keybase_result={}
            case_result={}
            result=[]
            targetdetail_result=[]
            portfolio_result=[]
            for a in json1_data:
                if a['type']=='case':
                    case_list_2.append(a['report_id'])
                else:
                    pass
            case_list_2=set(case_list_2) 
            for a in json1_data:
                if a['type']=='keybase':
                    keybase_list_2.append(a['report_id'])
                else:
                    pass
            keybase_list_2=set(keybase_list_2)

            for a in json1_data:
                if a['type']=='targetSummary':
                    targetSummary_list_2.append(a['report_id'])
                else:
                    pass
            targetSummary_list_2=set(targetSummary_list_2)  
            for a in json1_data:
                if a['type']=='targetDetail':
                    targetDetail_list_2.append(a['report_id'])
                else:
                    pass
            targetDetail_list_2=set(targetDetail_list_2)
            for a in json1_data:
                if a['type']=='portfolio':
                    portfolio_list_2.append(a['report_id'])
                else:
                    pass
            portfolio_list_2=set(portfolio_list_2)  
                 
            try:
                for each_data_in_id_caselist in case_list_2:
                    case_result={}
                    case_filter=ReportsNotes.objects.values().distinct('username').filter(type='case').filter(report_id=each_data_in_id_caselist).order_by('username','-date')
                    case_contributor=[]
                    for each_data_in_case_filter in case_filter:
                        case_contributor.append(each_data_in_case_filter['username'])
                    casedata=Case.objects.filter(id=each_data_in_id_caselist).first()
                    case_result['type']='case'
                    case_result['date']=case_filter[0]['date']
                    case_result['name']=casedata.case_title
                    case_result['contributors']=case_contributor
                    case_result['id']=each_data_in_id_caselist
                    result.append(case_result)
            except Exception as error :
                print(error)

            
                  
            try:
                for each_data_in_id_keylist in keybase_list_2:
                    keybase_result={}
                    keybase_filter=ReportsNotes.objects.values().distinct('username').filter(type='keybase').filter(report_id=each_data_in_id_keylist).order_by('username','-date')
                    keybase_contributor=[]
                    for each_data_in_keybase_filter in keybase_filter:
                        keybase_contributor.append(each_data_in_keybase_filter['username'])
                    targetdata=KeybaseTarget.objects.filter(GTR=each_data_in_id_keylist).first()
                    try:
                        keybaseid=targetdata.keybase_id
                        keybasedata=Keybase.objects.filter(id=keybaseid).first()    
                    except Exception as e:
                        # print(e)
                        pass
                    keybase_result['type']='keybase'
                    keybase_result['date']=keybase_filter[0]['date']
                    keybase_result['name']=keybasedata.title
                    keybase_result['contributors']=keybase_contributor
                    keybase_result['id']=each_data_in_id_keylist
                    result.append(keybase_result)
            except Exception as error :
                print(error)

           
        
    
            try:
                for each_data_in_id_summarylist in targetSummary_list_2:
                    targetSummary_result={}
                    targetSummary_filter=ReportsNotes.objects.values().distinct('username').filter(type='targetSummary').filter(report_id=each_data_in_id_summarylist).order_by('username','-date')
                    targetSummary_contributor=[]
                    for each_data_in_case_filter in targetSummary_filter:
                        targetSummary_contributor.append(each_data_in_case_filter['username'])
                    targetSummarydata=SocialTarget.objects.filter(GTR=each_data_in_id_summarylist).first()
                    targetSummary_result['type']='targetSummary'
                    targetSummary_result['date']=targetSummary_filter[0]['date']
                    targetSummary_result['name']=targetSummarydata.full_name
                    targetSummary_result['contributors']=targetSummary_contributor
                    targetSummary_result['id']=each_data_in_id_summarylist
                    result.append(targetSummary_result)
            except Exception as error :
                print(error)    

                
            try:
                for each_data_in_id_targetDetaillist in targetDetail_list_2:
                    targetDetail_result={}
                    targetDetail_filter=ReportsNotes.objects.values().distinct('username').filter(type='targetDetail').filter(report_id=each_data_in_id_targetDetaillist).order_by('username','-date')
                    targetDetail_contributor=[]
                    for each_data_in_targetDetail_filter in targetDetail_filter:
                        targetDetail_contributor.append(each_data_in_targetDetail_filter['username'])
                    targetDetaildata=SocialTarget.objects.filter(GTR=each_data_in_id_targetDetaillist).first()
                    targetDetail_result['type']='targetDetail'
                    targetDetail_result['date']=targetDetail_filter[0]['date']
                    targetDetail_result['name']=targetDetaildata.full_name
                    targetDetail_result['contributors']=targetDetail_contributor
                    targetDetail_result['id']=each_data_in_id_targetDetaillist
                    result.append(targetDetail_result)
            except Exception as error :
                print(error) 

              
            try:
                for each_data_in_id_portfoliolist in portfolio_list_2:
                    portfolioidindividual_dict={}
                    portfolioidgroup_dict={}
                    portfolioidevent_dict={}
                    portfolio_filter=ReportsNotes.objects.values().distinct('username').filter(type='portfolio').filter(report_id=each_data_in_id_portfoliolist).order_by('username','-date')
                    portfolio_contributor=[]
                    for each_data_in_portfolio_filter in portfolio_filter:
                        portfolio_contributor.append(each_data_in_portfolio_filter['username'])
                    targetdata1=Individual.objects.filter(id=each_data_in_id_portfoliolist).first()
                    portfoliodata2=Event.objects.filter(id=each_data_in_id_portfoliolist).first()
                    targetdata3=Group.objects.filter(id=each_data_in_id_portfoliolist).first()   
                    try:
                        if targetdata1:
                            portfolioidindividual=targetdata1.title
                            portfolioidindividual_dict['name']= portfolioidindividual
                            portfolioidindividual_dict['date']=portfolio_filter[0]['date']
                            portfolioidindividual_dict['type']='portfolio'
                            portfolioidindividual_dict['contributors']=portfolio_contributor
                            portfolioidindividual_dict['id']=each_data_in_id_portfoliolist
                            result.append(portfolioidindividual_dict)
                            
                        if targetdata3:     
                            portfolioidgroup=targetdata3.title
                            portfolioidgroup_dict['name']= portfolioidgroup
                            portfolioidgroup_dict['date']=portfolio_filter[0]['date']
                            portfolioidgroup_dict['type']='portfolio'
                            portfolioidgroup_dict['contributors']=portfolio_contributor
                            portfolioidgroup_dict['id']=each_data_in_id_portfoliolist
                            result.append(portfolioidgroup_dict)
                        
                        if portfoliodata2: 
                            portfolioidevent=portfoliodata2.title
                            portfolioidevent_dict['name']= portfolioidevent
                            portfolioidevent_dict['date']=portfolio_filter[0]['date']
                            portfolioidevent_dict['type']='portfolio'
                            portfolioidevent_dict['contributors']=portfolio_contributor
                            portfolioidevent_dict['id']=each_data_in_id_portfoliolist
                            result.append(portfolioidevent_dict)
                                
                            
                    except Exception as error:
                        print(error)
                     
                    # portfolio_result['type']='portfolio'
                    # portfolio_result['date']=portfolio_filter[0]['date']
                    # portfolio_result['target_name']=portfoliodata.full_name
                    # portfolio_result['contributors']=portfolio_contributor
                    # portfolio_result['case_id']=each_data_in_id_portfoliolist
                    # portfolio_result.append(portfolio_result)
            except Exception as error :
                print(error)    

            
            # for a in json1_data:
            #     if a['type']=='portfolio':
            #         targetDetail_list_2.append(a['report_id'])
            #     else:
            #         pass
            # targetDetail_list_2=set(targetDetail_list_2)      
            # try:
            #     for each_data_in_id_targetDetaillist in targetDetail_list_2:
            #         targetDetail_result={}
            #         targetDetail_filter=ReportsNotes.objects.values().distinct('username').filter(type='targetDetail').filter(report_id=each_data_in_id_targetDetaillist).order_by('username','-date')
            #         targetDetail_contributor=[]
            #         for each_data_in_targetDetail_filter in targetDetail_filter:
            #             targetDetail_contributor.append(each_data_in_targetDetail_filter['username'])
            #         targetDetaildata=SocialTarget.objects.filter(GTR=each_data_in_id_targetDetaillist).first()
            #         targetDetail_result['type']='targetDetail'
            #         targetDetail_result['date']=targetDetail_filter[0]['date']
            #         targetDetail_result['target_name']=targetDetaildata.full_name
            #         targetDetail_result['contributors']=targetDetail_contributor
            #         targetDetail_result['case_id']=each_data_in_id_targetDetaillist
            #         result.append(targetDetail_filter)
            # except Exception as error :
            #     print(error)    

                    

    
                    
        #         elif a['type']=='portfolio':
        #                 reportidcase=a['report_id']
        #                 print(reportidcase)
        #                 targetdata1=Individual.objects.filter(id=reportidcase).first()
        #                 portfoliodata2=Event.objects.filter(id=reportidcase).first()
        #                 targetdata3=Group.objects.filter(id=reportidcase).first()

        #                 try:
        #                     if targetdata1:
        #                         portfolioidindividual=targetdata1.title
        #                         data_dict2['name']= portfolioidindividual
        #                         data_dict2['date']=targetdata1.created_on
        #                         data_dict2['note']=a['note']
        #                         data_dict2['type']='portfolio'
        #                         data_dict2['commented_date']=a['date']
        #                         data_dict2['contributor']=a['username']
        #                         list_1.append(data_dict2)
        #                     if targetdata3:     
        #                         portfolioidgroup=targetdata3.title
        #                         data_dict22['name']= portfolioidgroup
        #                         data_dict22['date']=targetdata3.created_on
        #                         data_dict22['note']=a['note']
        #                         data_dict22['type']='portfolio'
        #                         data_dict22['commented_date']=a['date']
        #                         data_dict22['contributor']=a['username']
        #                         list_1.append(data_dict22)
                          
        #                     if portfoliodata2: 
        #                         portfolioidevent=portfoliodata2.title
        #                         data_dict23['name']= portfolioidevent
        #                         data_dict23['date']=portfoliodata2.created_on
        #                         data_dict23['note']=a['note']
        #                         data_dict23['type']='portfolio'
        #                         data_dict23['commented_date']=a['date']
        #                         data_dict23['contributor']=a['username']
        #                         list_1.append(data_dict23)
                                   
                            
        #                 except:
        #                        pass
                    
                 
       

             
           
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

                
        response = {
            'result': (result)
        }
        return Response(response)     

class BriefView(viewsets.ViewSet):

    authentication_classes = (TokenAuthentication,)

    def get_briefs(self, request):
        user = request.user
        final_dict = {}
        report_type = []
        briefs_by_user = []
        user_list = []

        try:
            type = request.data['type']
            report_id = request.data['report_id']

        except Exception as error:
            response = {
                'error': str(error)
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = Brief.objects.filter(type=type).filter(report_id=report_id).values()

            for r in result:
                final_dict['name'] = r['username']
                # final_dict['type'] = r['type']
                user_list.append(r['username'])
                report_type.append(r['type'])
                # notes_by_user.append(ReportsNotes.objects.filter(username=r['username']).values('note', 'date'))
                # final_dict['notes'] = ReportsNotes.objects.filter(username=r['username']).values('note', 'date')
            user_list = set(user_list)
            user_list = list(user_list)
            # report_type = set(report_type)
            # report_type = list(report_type)

            for user in user_list:
                final_dict['name'] = user

                final_dict['briefs'] = Brief.objects.filter(username=user).filter(type=type).filter(
                    report_id=report_id).values('brief', 'date')
                briefs_by_user.append(final_dict)
                final_dict = {}

            #
            # notes.append(final_dict)
            print(final_dict)
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'result': result,
            'user_list': briefs_by_user,
             'current_user': str(user)
        }
        return Response(response, status=status.HTTP_200_OK)

    def add_briefs(self, request):
        try:
            report_id = request.data['report_id']
            type = request.data['type']
            brief = request.data['brief']
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)
        print(request.data)
        try:
            Brief.objects.create(report_id=report_id, type=type, username=request.user, brief=brief)

        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)

        response = {
            'message': 'Note added on report'
        }
        return Response(response)


