from django.http import response
from requests.sessions import extract_cookies_to_jar
from .serializers import *
from .models import LinkedData, Individual, Group, Event
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, DjangoModelPermissions
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User
import datetime
import json
from case_management.models import Case
from rest_framework.response import Response
from rest_framework import status
from django.contrib.contenttypes.fields import ContentType
from rest_framework.decorators import action
from django.db import IntegrityError, InternalError
from keybase_management.models import Keybase
from target_management.models import SocialTarget, KeybaseTarget, GenericTarget
from rest_framework.pagination import PageNumberPagination, LimitOffsetPagination
from .serializers import NewIndividualSerializer, NewIndividualSerializerV1
from rest_framework.exceptions import PermissionDenied,NotAuthenticated
import json
from rest_framework.renderers import JSONRenderer
from django.core.paginator import Paginator
import math
import itertools
class StandardResultsSetPagination(LimitOffsetPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 5


def perform_date_change(serializer):
    serializer_copy = serializer.copy()
    if 'expire_on' in serializer_copy:
        expire_date = datetime.datetime.fromtimestamp(
            float(serializer_copy['expire_on']) / 1000) + datetime.timedelta(hours=11)
        serializer_copy.update({'expire_on': expire_date})
    if 'address' in serializer_copy:
        address = str(serializer_copy['address'])
        serializer_copy.update({'address': address})
    if 'phone_number' in serializer_copy:
        phone_number = str(serializer_copy['phone_number'])
        serializer_copy.update({'phone_number': phone_number})
    if 'date_of_birth' in serializer_copy:
        date_of_birth = datetime.date.fromtimestamp(
            float(serializer_copy['date_of_birth']) / 1000)
        serializer_copy.update({'date_of_birth': date_of_birth})
    if 'event_date' in serializer_copy:
        event_date = datetime.datetime.fromtimestamp(
            float(serializer_copy['event_date']) / 1000)
        serializer_copy.update({'event_date': event_date})
    if 'content_type' and 'id' in serializer_copy:
        if serializer_copy['content_type'] == 'social':
            target_object = SocialTarget.objects.get(id=int(serializer_copy['id']))
            print(ContentType.objects.get_for_model(target_object))
            serializer_copy.update({'content_type': int(ContentType.objects.get_for_model(target_object).id)})
            serializer_copy.update({'content_object': target_object})

    if 'keywords' in serializer_copy:
        print(serializer_copy['keywords'])
    return serializer_copy


class IndividualViewSet(viewsets.ModelViewSet):

    #queryset = Individual.objects.all().order_by('-created_on')
    pagination_class = StandardResultsSetPagination
    permission_classes = (DjangoModelPermissions, IsAuthenticated)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return self.request.user.individual_set.all().order_by('-created_on')

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return IndividualSerializer
        return IndividualSerializer

    def create(self, request, *args, **kwargs):
        # auth_user = request.user.has_perm("portfolio_management.can_create_individual_portfolio")
        # print(auth_user)
        # if auth_user == False:
        #     response = {
        #         'message': 'permission missing',
        #         'status': False,
        #         'result': None
        #         }
        #     return Response(response,status=status.HTTP_403_FORBIDDEN)
        if request.data:
            try:
                if Individual.objects.filter(title=request.data['title']).exists():
                    response = {
                        'message': 'Individual Portfolio already exists!'
                    }
                    return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)

                data = perform_date_change(request.data)
                serializer = IndividualSerializer(data=data)
                serializer.is_valid(raise_exception=True)
                if Individual.get_individual_portfolio_count():
                    serializer.save()
                    headers = self.get_success_headers(serializer.data)
                    response = {
                        'message': 'Portfolio Created Successfully',
                        'status': True,
                        'result': serializer.data
                    }
                    return Response(response, status=status.HTTP_201_CREATED, headers=headers)
                else:
                    response = {
                        'message': 'Individual Portfolio Exceed for today'
                    }
                    return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)


            except IntegrityError:
                import traceback
                traceback.print_exc()
                response = {
                    'message': 'Conflict',
                    'status': False,
                    'result': None
                }
                return Response(response, status=status.HTTP_409_CONFLICT)

            except Exception as E:
                import traceback
                traceback.print_exc()
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': str(E)
                }
                return Response(response,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {
                'message': 'Please provide the data',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_400_BAD_REQUEST)

    def list(self, request, *args, **kwargs):
        # auth_user = request.user.has_perm("portfolio_management.can_access_individual_portfolio")
        # print(auth_user)
        # if auth_user == False:
        #     response = {
        #         'message': 'permission missing',
        #         'status': False,
        #         'result': None
        #         }
        #     return Response(response,status=status.HTTP_403_FORBIDDEN)
        queryset = self.filter_queryset(self.get_queryset())
        # page = self.paginate_queryset(queryset)
        # if page is not None:
        #     serializer = self.get_serializer(page, many=True)
        #     data_dict = serializer.data.copy()
        #     print(data_dict)
        #     return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        # data_resp = serializer.data
        return Response({"results":serializer.data})

    def all_portfolio(self, request):
        # auth_user = request.user.has_perm("portfolio_management.can_access_linked_info")
        # print(auth_user)
        # if auth_user == False:
        #     return Response('Permission not givenn')
        try:
            id = request.data['id']
            type = request.data['type']
        except Exception as error:
            response = {
                'message': str(error)
            }
            return Response(response)
        try:

            if type == 'individual':
                obj = Individual.objects.filter(id=id)
                ser = NewIndividualSerializer(obj, many=True)

            elif type == 'group':
                obj = Group.objects.filter(id=id)
                ser = GroupSerializerV1(obj, many=True)

            elif type == 'event':
                obj = Event.objects.filter(id=id)
                ser = EventSerializerV1(obj, many=True)
                
            sorted_ser =  ser.data.copy()
            linked_data_categorization = []
            if "linked_data" in ser.data[0]:
                for linked_data in ser.data[0]["linked_data"]:
                    if linked_data["type_update"] == "post_data":
                        if "categorization" in linked_data["data"]:
                            linked_data_categorization.append(linked_data["data"]["categorization"]["predictions"][0])
            ser.data[0]["categorization"] = set(linked_data_categorization)
            sorted_ser  = sorted(ser.data[0]["linked_data"], key=lambda x: x['data']['created_on'] if x['type'] == 'post_data' else 0,reverse=True)
            ser.data[0]["linked_data"] = sorted_ser



            return Response(ser.data)
        except Exception as error:
            respone = {
                'message': str(error)
            }
            return Response(respone)

    def portfolio_pagination(self, request):
        
        type_ = self.request.query_params.get('type')
        page = self.request.query_params.get('page')
        title = self.request.query_params.get('title')
        user = request.user
        
        if type_:
            if type_ == 'individual':
                if not request.user.is_superuser:

                    query = Q(user=user)
                    query.add(Q(share_resource__contains=[user.id]), Q.OR)
                    if title:
                        query.add(Q(title__icontains=title), Q.AND)

                    obj = Individual.objects.filter(query).order_by('-created_on')
                    obj_count = Individual.objects.filter(query).count()

                else:

                    if title:
                        query = Q(title__icontains=title)

                        obj = Individual.objects.filter(query).order_by('-created_on')
                        obj_count = Individual.objects.filter(query).count()
                    else:

                        obj = Individual.objects.all().order_by('-created_on')
                        obj_count = Individual.objects.all().count()

                
                paginator = Paginator(obj, 8)
                targets = paginator.page(int(page))
                result = NewIndividualSerializerV1(targets, many=True)

            elif type_ == 'group':

                if not request.user.is_superuser:
                    query = Q(user=user)
                    query.add(Q(share_resource__contains=[user.id]), Q.OR)

                    if title:
                        query.add(Q(title__icontains=title), Q.AND)
                            
                    obj = Group.objects.filter(query).order_by('-created_on')
                    obj_count = Group.objects.filter(query).count()

                else:

                    if title:
                        query = Q(title__icontains=title)
                        
                        obj = Group.objects.filter(query).order_by('-created_on')
                        obj_count = Group.objects.filter(query).count()

                    else:

                        obj = Group.objects.all().order_by('-created_on')
                        obj_count = Group.objects.all().count()

                paginator = Paginator(obj, 8)
                targets = paginator.page(int(page))
                result = GroupSerializerV2(targets, many=True)

            elif type_ == 'event':

                if not request.user.is_superuser:
                    query = Q(user=user)
                    query.add(Q(share_resource__contains=[user.id]), Q.OR)

                    if title:
                        
                        query.add(Q(title__icontains=title), Q.AND)

                    obj = Event.objects.filter(query).order_by('-created_on')
                    obj_count = Event.objects.filter(query).count()
                
                else:

                    if title:
                        query = Q(title__icontains=title)

                        obj = Event.objects.filter(query).order_by('-created_on')
                        obj_count = Event.objects.filter(query).count()

                    else:

                        obj = Event.objects.all().order_by('-created_on')
                        obj_count = Event.objects.all().count()
                    
                paginator = Paginator(obj, 8)
                targets = paginator.page(int(page))
                result = EventSerializerV2(targets, many=True)
        if result:
            # result = SocialTargetListSerializerV1(targets, many = True)
            response = {'message': 'List all the Targets',
                        'status': True,
                        'targets_count':obj_count,
                        "pages": math.ceil(obj_count/8),
                        "current_page":int(page),
                        'result': result.data,
                        }
            return Response(response,
                            status=status.HTTP_200_OK)

    def portfolio_detail(self, request, *args, **kwargs):
        id = kwargs['id']
        type = kwargs['type']
        address = []
        phone_numbers = []
        if type == 'individual':
            portfolio_obj = Individual.objects.filter(id=id).values()
            for obj in portfolio_obj:
                if obj['address'] != '[]':
                    for o in obj['address'].strip('[]').split(','):
                        o = o.replace(' ', '')
                        o = o.replace("'", '"')
                        # address.append(json.loads(o))
                        address.append(o)
                        obj['address'] = address
                if obj['phone_number'] != '[]':
                    for o in obj['phone_number'].strip('[]').split(','):
                        o = o.replace(' ', '')
                        o = o.replace("'", '"')
                        # phone_numbers.append(json.loads(o))
                        phone_numbers.append(o)
                        obj['phone_number'] = phone_numbers
        if type == 'group':
            portfolio_obj = Group.objects.filter(id=id).values()
            print(portfolio_obj)
            for obj in portfolio_obj:
                if obj['address'] != '[]':
                    for o in obj['address'].strip('[]').split(','):
                        o = o.replace(' ', '')
                        o = o.replace("'", '"')
                        # obj['address'] = address.append(json.loads(o))
                        obj['address'] = address.append(o)
                        obj['address'] = address
                if obj['phone_number'] != '[]':
                    for o in obj['phone_number'].strip('[]').split(','):
                        o = o.replace(' ', '')
                        o = o.replace("'", '"')
                        # phone_numbers.append(json.loads(o))
                        phone_numbers.append(o)
                        obj['phone_number'] = phone_numbers

        if type == 'event':
            portfolio_obj = Event.objects.filter(id=id).values()
            for obj in portfolio_obj:
                if obj['address'] != '[]':
                    for o in obj['address'].strip('[]').split(','):
                        o = o.replace(' ', '')
                        o = o.replace("'", '"')
                        # address.append(json.loads(o))
                        address.append(o)
                        obj['address'] = address
                if obj['phone_number'] != '[]':
                    for o in obj['phone_number'].strip('[]').split(','):
                        o = o.replace(' ', '')
                        # print(o)
                        o = o.replace("'", '"')
                        # phone_numbers.append(json.loads(o))
                        phone_numbers.append(o)
                        obj['phone_number'] = phone_numbers

        response = {
            'result': portfolio_obj
        }
        return Response(response)

    def update(self, request, *args, **kwargs):
        if 'portfolio_id' in request.query_params:
            portfolio_id = str(request.query_params['portfolio_id'])
            print(portfolio_id)
        else:
            portfolio_id = None
        update_detail = perform_date_change(request.data)
        print('update', update_detail)
        if all(v is not None for v in [portfolio_id, update_detail]):
            if Individual.objects.filter(id=portfolio_id):
                portfolio = Individual.objects.filter(id=portfolio_id).first()
            else:
                portfolio = None
            if portfolio is None:
                response = {
                    'message': 'Portfolio object not found for selected target',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_204_NO_CONTENT)
            try:
                for attr, value in update_detail.items():
                    setattr(portfolio, attr, value)
                updated = portfolio.update()
                if updated:
                    result = self.get_serializer_class()(
                        instance=portfolio,
                        many=False).data
                else:
                    result = None
                response = {
                    'message': 'Updated Successfully',
                    'status': True,
                    'result': result
                }

                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Url Already found',
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
    def attach_keybase(self, request):

        user = request.user

        print("Request By User: ", user)

        data_dict = request.data.copy()
        keys = [*data_dict]

        if set(keys) == {'keybase_id', 'portfolio_id', 'portfolio_type', 'operation'}:
            keybase_id, portfolio_id, portfolio_type, operation = \
                data_dict['keybase_id'], data_dict['portfolio_id'], data_dict['portfolio_type'], data_dict['operation']
            try:
                if portfolio_type == 'individual':
                    if Individual.objects.filter(id=portfolio_id):
                        portfolio = Individual.objects.filter(id=portfolio_id).first()
                        serializer = IndividualSerializerV1
                    else:
                        portfolio, serializer = None, None
                elif portfolio_type == 'group':
                    if Group.objects.filter(id=portfolio_id):
                        portfolio = Group.objects.filter(id=portfolio_id).first()
                        serializer = GroupSerializerV1
                    else:
                        portfolio, serializer = None, None
                elif portfolio_type == 'event':
                    if Event.objects.filter(id=portfolio_id):
                        portfolio = Event.objects.filter(id=portfolio_id).first()
                        serializer = EventSerializerV1
                    else:
                        portfolio, serializer = None, None
                else:
                    portfolio, serializer = None, None
                if portfolio is None:
                    response = {
                        'message': 'Target object not found for selected target',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                keybase = Keybase.objects.filter(id=keybase_id).first()
                if operation == 'attach':

                    updated = portfolio.keybase.add(keybase)

                else:
                    updated = portfolio.keybase.remove(keybase)
                if updated:
                    result = serializer(
                        instance=portfolio,
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

    @action(detail=True, methods=['POST'])
    def attach_case(self, request):
        user = request.user
        print("Request By User: ", user)
        data_dict = request.data.copy()
        keys = [*data_dict]
        if set(keys) == {'case_id', 'portfolio_id', 'portfolio_type', 'operation'}:
            case_id, portfolio_id, portfolio_type, operation = \
                data_dict['case_id'], data_dict['portfolio_id'], data_dict['portfolio_type'], data_dict['operation']
            try:
                if portfolio_type == 'individual':
                    if Individual.objects.filter(id=portfolio_id):
                        portfolio = Individual.objects.filter(id=portfolio_id).first()
                        serializer = IndividualSerializerV1
                    else:
                        portfolio, serializer = None, None
                elif portfolio_type == 'group':
                    if Group.objects.filter(id=portfolio_id):
                        portfolio = Group.objects.filter(id=portfolio_id).first()
                        serializer = GroupSerializerV1
                    else:
                        portfolio, serializer = None, None
                elif portfolio_type == 'event':
                    if Event.objects.filter(id=portfolio_id):
                        portfolio = Event.objects.filter(id=portfolio_id).first()
                        serializer = EventSerializerV1
                    else:
                        portfolio, serializer = None, None
                else:
                    portfolio, serializer = None, None
                if portfolio is None:
                    response = {
                        'message': 'Target object not found for selected target',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                case = Case.objects.filter(id=case_id).first()
                if operation == 'attach':
                    updated = portfolio.case.add(case)
                else:
                    updated = portfolio.case.remove(case)
                if updated:
                    result = serializer(
                        instance=portfolio,
                        many=False).data
                else:
                    result = None
                response = {
                    'message': 'Case attach Successfully',
                    'status': True,
                    'result': result
                }
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Case url Already found',
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
    def attach_target(self, request):
        user = request.user
        print("Request By User: ", user)
        data_dict = request.data.copy()
        keys = [*data_dict]
        if set(keys) == {'target_id', 'target_type', 'portfolio_id', 'portfolio_type', 'operation'}:
            target_id, target_type, portfolio_id, portfolio_type, operation = \
                data_dict['target_id'], data_dict['target_type'], data_dict['portfolio_id'], \
                data_dict['portfolio_type'], data_dict['operation']
            try:
                if portfolio_type == 'individual':
                    if Individual.objects.filter(id=portfolio_id):
                        portfolio = Individual.objects.filter(id=portfolio_id).first()
                        serializer = IndividualSerializerV1
                    else:
                        portfolio, serializer = None, None
                elif portfolio_type == 'group':
                    if Group.objects.filter(id=portfolio_id):
                        portfolio = Group.objects.filter(id=portfolio_id).first()
                        serializer = GroupSerializerV1
                    else:
                        portfolio, serializer = None, None
                elif portfolio_type == 'event':
                    if Event.objects.filter(id=portfolio_id):
                        portfolio = Event.objects.filter(id=portfolio_id).first()
                        serializer = EventSerializerV1
                    else:
                        portfolio, serializer = None, None
                else:
                    portfolio, serializer = None, None
                if portfolio is None:
                    response = {
                        'message': 'Target object not found for selected target',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                if target_type == 'social':
                    target = SocialTarget.objects.filter(id=target_id).first()
                elif target_type == 'generic':
                    target = GenericTarget.objects.filter(id=target_id).first()
                elif target_type == 'keybase':
                    target = KeybaseTarget.objects.filter(id=target_id).first()
                else:
                    target = None
                if operation == 'attach' and target:
                    updated = portfolio.target.add(target)
                else:
                    updated = portfolio.target.remove(target)
                if updated:
                    result = serializer(
                        instance=portfolio,
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

    @action(detail=True, methods=['POST'])
    def attach_portfolio(self, request):
        user = request.user
        print("Request By User: ", user)
        data_dict = request.data.copy()
        keys = [*data_dict]
        if set(keys) == {'portfolio_id_src', 'portfolio_type_src',
                         'portfolio_id_des', 'portfolio_type_des', 'operation'}:
            portfolio_id_s, portfolio_type_s, portfolio_id_d, portfolio_type_d, operation = \
                data_dict['portfolio_id_src'], data_dict['portfolio_type_src'], data_dict['portfolio_id_des'], \
                data_dict['portfolio_type_des'], data_dict['operation']
            try:
                if portfolio_type_s == 'individual':
                    if Individual.objects.filter(id=portfolio_id_s):
                        portfolio_src = Individual.objects.filter(id=portfolio_id_s).first()
                        serializer = IndividualSerializerV1
                    else:
                        portfolio_src, serializer = None, None
                elif portfolio_type_s == 'group':
                    if Group.objects.filter(id=portfolio_id_s):
                        portfolio_src = Group.objects.filter(id=portfolio_id_s).first()
                        serializer = GroupSerializerV1
                    else:
                        portfolio_src, serializer = None, None
                elif portfolio_type_s == 'event':
                    if Event.objects.filter(id=portfolio_id_s):
                        portfolio_src = Event.objects.filter(id=portfolio_id_s).first()
                        serializer = EventSerializerV1
                    else:
                        portfolio_src, serializer = None, None
                else:
                    portfolio_src, serializer = None, None
                if portfolio_src is None:
                    response = {
                        'message': 'portfolio object not found for selected portfolio',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                if portfolio_type_d == 'individual':
                    portfolio = Individual.objects.filter(id=portfolio_id_d).first()
                elif portfolio_type_d == 'group':
                    portfolio = Group.objects.filter(id=portfolio_id_d).first()
                elif portfolio_type_d == 'event':
                    portfolio = Event.objects.filter(id=portfolio_id_d).first()
                else:
                    portfolio = None
                if operation == 'attach' and portfolio:
                    updated = portfolio_src.portfolio.add(portfolio)
                else:
                    updated = portfolio_src.portfolio.remove(portfolio)
                if updated:
                    result = serializer(
                        instance=portfolio_src,
                        many=False).data
                else:
                    result = None
                response = {
                    'message': 'portfolio Updated Successfully',
                    'status': True,
                    'result': result
                }
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'portfolio url Already found',
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
        user = request.user
        print("Data------", request.data)
        print("Request By User: ", user)
        data_dict = request.data.copy()
        keys = [*data_dict]
        if set(keys) == {'data_id', 'portfolio_id', 'portfolio_type', 'operation'}:
            data_id, portfolio_id, portfolio_type, operation = \
                data_dict['data_id'], data_dict['portfolio_id'], data_dict['portfolio_type'], data_dict['operation']
            try:
                if portfolio_type == 'individual':
                    if Individual.objects.filter(id=portfolio_id):
                        portfolio = Individual.objects.filter(id=portfolio_id).first()
                        serializer = IndividualSerializerV1
                    else:
                        portfolio, serializer = None, None
                elif portfolio_type == 'group':
                    if Group.objects.filter(id=portfolio_id):
                        portfolio = Group.objects.filter(id=portfolio_id).first()
                        serializer = GroupSerializerV1
                    else:
                        portfolio, serializer = None, None
                elif portfolio_type == 'event':
                    if Event.objects.filter(id=portfolio_id):
                        portfolio = Event.objects.filter(id=portfolio_id).first()
                        serializer = EventSerializerV1
                    else:
                        portfolio, serializer = None, None
                else:
                    portfolio, serializer = None, None
                if portfolio is None:
                    response = {
                        'message': 'Target object not found for selected target',
                        'status': False,
                        'result': None
                    }
                    return Response(response,
                                    status=status.HTTP_204_NO_CONTENT)
                linked_data = LinkedData.objects.filter(id=data_id).first()

                if operation == 'attach' and linked_data:
                    updated = portfolio.linked_data.add(linked_data)
                else:
                    updated = portfolio.linked_data.remove(linked_data)
                if updated:
                    result = serializer(
                        instance=portfolio,
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


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all().order_by('-created_on')
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    authentication_classes = (TokenAuthentication,)
    pagination_class = StandardResultsSetPagination



    def get_queryset(self):
        return self.request.user.group_set.all().order_by('-created_on')


    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return GroupSerializerV1
        return GroupSerializer

    def list(self, request):
        queryset = self.get_queryset()
    
        serializer = self.get_serializer(queryset, many=True)
        return Response({"results":serializer.data})

    def create(self, request, *args, **kwargs):
        # auth_user = request.user.has_perm("portfolio_management.can_create_group_portfolio")
        # print(auth_user)
        # if auth_user == False:
        #     response = {
        #         'message': 'permission missing',
        #         'status': False,
        #         'result': None
        #         }
        #     return Response(response,status=status.HTTP_403_FORBIDDEN)
        if request.data:
            try:
                # print('data', request.data)
                if Group.objects.filter(title=request.data['title']).exists():
                    response = {
                        'message': 'Group Portfolio already exists!'
                    }
                    return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
                data = perform_date_change(request.data)
                portfolio = Group()
                for attr, value in data.items():
                    setattr(portfolio, attr, value)
                    print('Attribute', attr)
                    print('Value', value)

                if Group.get_group_portfolio_count():
                    created = portfolio.save()
                    if created:
                        result = self.get_serializer_class()(
                            instance=portfolio,
                            many=False).data
                    else:
                        result = None
                    print(result)
                    response = {
                        'message': 'Portfolio Created Successfully',
                        'status': True,
                        'result': result
                    }
                    return Response(response,
                                    status=status.HTTP_200_OK)
                else:
                    response = {
                        'message': 'Limit Exceed for today'
                    }
                    return Response(response)
            except IntegrityError:
                response = {
                    'message': 'Conflict',
                    'status': False,
                    'result': None
                }
                return Response(response, status=status.HTTP_409_CONFLICT)

            except Exception as E:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': str(E)
                }
                return Response(response,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {
                'message': 'Please provide the data',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        if 'portfolio_id' in request.query_params:
            portfolio_id = str(request.query_params['portfolio_id'])
            print(portfolio_id)
        else:
            portfolio_id = None
        update_detail = perform_date_change(request.data)
        print('update', update_detail)
        if all(v is not None for v in [portfolio_id, update_detail]):
            if Group.objects.filter(id=portfolio_id):
                portfolio = Group.objects.filter(id=portfolio_id).first()
            else:
                portfolio = None
            if portfolio is None:
                response = {
                    'message': 'Portfolio object not found for selected target',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_204_NO_CONTENT)
            try:
                for attr, value in update_detail.items():
                    setattr(portfolio, attr, value)
                updated = portfolio.update()
                if updated:
                    result = self.get_serializer_class()(
                        instance=portfolio,
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


class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all().order_by('-created_on')
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    authentication_classes = (TokenAuthentication,)
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return self.request.user.event_set.all().order_by('-created_on')

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return EventSerializerV1
        return EventSerializer

    def list(self, request):
        queryset = self.get_queryset()
    
        serializer = self.get_serializer(queryset, many=True)
        return Response({"results":serializer.data})

    def create(self, request, *args, **kwargs):
        # auth_user = request.user.has_perm("portfolio_management.can_create_event_portfolio")
        # print(auth_user)
        # if auth_user == False:
        #     response = {
        #         'message': 'permission missing',
        #         'status': False,
        #         'result': None
        #         }
        #     return Response(response,status=status.HTTP_403_FORBIDDEN)
        if request.data:
            print('----------------', request.data, '-----------------')
            try:
                # print('data', request.data)
                if Event.objects.filter(title=request.data['title']).exists():
                    response = {
                        'message': 'Event Portfolio already exists!'
                    }
                    return Response(response, status=status.HTTP_406_NOT_ACCEPTABLE)
                data = perform_date_change(request.data)
                portfolio = Event()
                for attr, value in data.items():
                    setattr(portfolio, attr, value)
                    print('Attribute', attr)
                    print('Value', value)

                if Event.get_events_portfolio_count():
                    created = portfolio.save()
                    if created:
                        result = self.get_serializer_class()(
                            instance=portfolio,
                            many=False).data
                    else:
                        result = None
                    print(result)
                    response = {
                        'message': 'Portfolio Created Successfully',
                        'status': True,
                        'result': result
                    }
                    return Response(response,
                                    status=status.HTTP_200_OK)
                else:
                    response = {
                        'message': 'Limit Exceed for today'
                    }
                    return Response(response)
            except IntegrityError:
                import traceback
                traceback.print_exc()
                response = {
                    'message': 'Conflict',
                    'status': False,
                    'result': None
                }
                return Response(response, status=status.HTTP_409_CONFLICT)

            except Exception as E:
                response = {
                    'message': 'Attribute Value missing',
                    'status': False,
                    'result': str(E)
                }
                return Response(response,
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {
                'message': 'Please provide the data',
                'status': False,
                'result': None
            }
            return Response(response,
                            status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        # auth_user = request.user.has_perm("portfolio_management.can_update_event_portfolio")
        # print(auth_user)
        # if auth_user == False:
        #     response = {
        #         'message': 'permission missing',
        #         'status': False,
        #         'result': None
        #         }
        #     return Response(response,status=status.HTTP_403_FORBIDDEN)
        if 'portfolio_id' in request.query_params:
            portfolio_id = str(request.query_params['portfolio_id'])
            print(portfolio_id)
        else:
            portfolio_id = None
        update_detail = perform_date_change(request.data)
        print('update', update_detail)
        if all(v is not None for v in [portfolio_id, update_detail]):
            if Event.objects.filter(id=portfolio_id):
                portfolio = Event.objects.filter(id=portfolio_id).first()
            else:
                portfolio = None
            if portfolio is None:
                response = {
                    'message': 'Portfolio object not found for selected target',
                    'status': False,
                    'result': None
                }
                return Response(response,
                                status=status.HTTP_204_NO_CONTENT)
            try:
                for attr, value in update_detail.items():
                    setattr(portfolio, attr, value)
                updated = portfolio.update()
                if updated:
                    result = self.get_serializer_class()(
                        instance=portfolio,
                        many=False).data
                else:
                    result = None
                response = {
                    'message': 'Updated Successfully',
                    'status': True,
                    'result': result
                }
                return Response(response,
                                status=status.HTTP_200_OK)
            except IntegrityError:
                response = {
                    'message': 'Url Already found',
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
    def portfolio_report(self, request,**kwargs):
        portfolio_dict={}
        try:
            type_ = self.request.query_params.get('type')
            id=kwargs['id']
            portfolio_list=[]
            if type_ == "individual":
                portfolio_data=Individual.objects.filter(id=id).first()
                serilized_data = NewIndividualSerializer(portfolio_data, many=False)
            elif type_ == "group":
                portfolio_data=Group.objects.filter(id=id).first()
                serilized_data = GroupSerializerV1(portfolio_data, many=False)
            elif type_ == "event":
                portfolio_data=Event.objects.filter(id=id).first()
                serilized_data = EventSerializerV1(portfolio_data, many=False)
            portfolio_json_data=JSONRenderer().render(serilized_data.data)
            portfolio_json_data_final = json.loads(portfolio_json_data)
            
            target_list=[]
            for data in portfolio_json_data_final['target']:
                if data["GTR"].split('_')[1]=='fb':
                    data["profile_"] = es_object.get_response_by_gtr_portfolio_report(index='facebook_profile_profile_information', gtr_id=data['GTR'])
                elif data["GTR"].split('_')[1]=='tw':
                    data["profile_"] = es_object.get_response_by_gtr_portfolio_report(index='twitter_profile_profile_information', gtr_id=data['GTR'])
                elif data["GTR"].split('_')[1]=='ln':
                    data["profile_"] = es_object.get_response_by_gtr_portfolio_report(index='linkedin_profile_profile_information', gtr_id=data['GTR'])
                elif data["GTR"].split('_')[1]=='in':
                    data["profile_"] = es_object.get_response_by_gtr_portfolio_report(index='instagram_profile_profile_information', gtr_id=data['GTR'])
                elif data["GTR"].split('_')[1]=='tk':
                    data["profile_"] = es_object.get_response_by_gtr_portfolio_report(index='tiktok_profile_profile_information', gtr_id=data['GTR'])
                elif data["GTR"].split('_')[1]=='sc':
                    data["profile_"] = es_object.get_response_by_gtr_portfolio_report(index='snapchat_profile_profile_information', gtr_id=data['GTR'])
                elif data["GTR"].split('_')[1]=='tb':
                    data["profile_"] = es_object.get_response_by_gtr_portfolio_report(index='tumblr_profile_profile_information', gtr_id=data['GTR'])
                elif data["GTR"].split('_')[1]=='rd':
                    data["profile_"] = es_object.get_response_by_gtr_portfolio_report(index='reddit_profile_profile_information', gtr_id=data['GTR'])     

                target_list.append(data)
          
            portfolio_dict['details']=portfolio_json_data_final
            keybase_list=[]
            phrases_list=[]
            hashtag_list=[]
            mentions_list=[]
            for data in portfolio_json_data_final['keybase']:
                keybase_list.append(data)
            # print(keybase_list)
            portfolio_dict['details']=portfolio_json_data_final
            result_data={}
            date_list=[]
            prediction_list=[]
            emotion_list=[]
            sentiment_list=[]
            key_list=[]
            
            keybase_list_total=[]
          
            try:
                for data in keybase_list:
                    key_list.append(data['keywords'])
                keybase_list_total=list(itertools.chain(*key_list))
                dict_for_keybase={}
                for make_keys in keybase_list_total:
                    dict_for_keybase[make_keys]=0
                for  data_keybase in keybase_list_total:
                    dict_for_keybase[data_keybase]=dict_for_keybase[data_keybase]+1
                final_keyword_dict=[{'tag':key,"count":value} for key,value in dict_for_keybase.items()]
                
                pass
            except :
                pass
            final_phrases_dict = []
            try:
                phrases_list_total=[]
                for data in keybase_list:
                    phrases_list.append(data['phrases'])
                phrases_list_total=list(itertools.chain(*phrases_list))
                dict_for_phrases={}
                for make_keys in phrases_list_total:
                    dict_for_phrases[make_keys]=0
                for  data_phrases in phrases_list_total:
                    dict_for_phrases[data_phrases]=dict_for_phrases[data_phrases]+1
                    final_phrases_dict=[{'tag':key,"count":value} for key,value in dict_for_phrases.items()]
               
                pass
            except :
                pass
            final_mention_dict = []
            try:
                mentions_list_total=[]
                for data in keybase_list:
                    mentions_list.append(data['mentions'])
                mentions_list_total=list(itertools.chain(*mentions_list))
                dict_for_mentions={}
                for make_keys in mentions_list_total:
                    dict_for_mentions[make_keys]=0
                for  data_mention in mentions_list_total:
                    dict_for_mentions[data_mention]=dict_for_mentions[data_mention]+1
                    final_mention_dict=[{'tag':key,"count":value} for key,value in dict_for_mentions.items()]
                
                
                pass
            except :
                pass
            final_hashtags_dict = []
            try:
                hashtags_list_total=[]
                for data in keybase_list:
                    hashtag_list.append(data['hashtags'])
                hashtags_list_total=list(itertools.chain(*hashtag_list))
                dict_for_hashtag={}
                for make_keys in hashtags_list_total:
                    dict_for_hashtag[make_keys]=0
                for  data_hashtags in hashtags_list_total:
                    dict_for_hashtag[data_hashtags]=dict_for_hashtag[data_hashtags]+1
                    final_hashtags_dict=[{'tag':key,"count":value} for key,value in dict_for_hashtag.items()]
                
                pass
            except :
                pass
            list_word_cloud=[]
            list_common_words=[]
            final_wordcloud_dict = []
            try:
                for data_each in portfolio_json_data_final['target']:
                    gtr_data=(data_each['GTR'])
                    if gtr_data.split('_')[0]=='st':
                        if gtr_data.split('_')[1]=='fb':
                            res_data_mining=es_object.get_response_by_gtr_portfolio_report(index='facebook_*_data_mining', gtr_id=data_each['GTR']) 
                            if res_data_mining:
                                for data in res_data_mining:
                                    if data['algorithm_type']=='word_cloud':
                                        list_word_cloud.append(data['string_attributes'])
                                        if data['algorithm_type']=='common_words':
                                            list_common_words.append(data['list_attributes'])
                                        else:
                                            pass    

                                    elif data['algorithm_type']=='common_words':
                                        list_common_words.append(data['list_attributes'])
                                        
                               
                            else:
                                pass
                        elif gtr_data.split('_')[1]=='tw':
                            res_data_mining=es_object.get_response_by_gtr_portfolio_report(index='twitter_profile_data_mining', gtr_id=data_each['GTR']) 
                            if res_data_mining:
                                for data in res_data_mining:
                                    if data['algorithm_type']=='word_cloud':
                                        list_word_cloud.append(data['string_attributes'])
                                        if data['algorithm_type']=='common_words':
                                            list_common_words.append(data['list_attributes'])
                                        else:
                                            pass
                                    elif data['algorithm_type']=='common_words':
                                        list_common_words.append(data['list_attributes'])
                            else:
                                pass
                        elif gtr_data.split('_')[1]=='ln':
                            res_data_mining=es_object.get_response_by_gtr_portfolio_report(index='linkedin_*_data_mining', gtr_id=data_each['GTR']) 
                            if res_data_mining:
                                for data in res_data_mining:
                                    if data['algorithm_type']=='word_cloud':
                                        list_word_cloud.append(data['string_attributes'])
                                        if data['algorithm_type']=='common_words':
                                            list_common_words.append(data['list_attributes'])
                                        else:
                                            pass
                                    elif data['algorithm_type']=='common_words':
                                        list_common_words.append(data['list_attributes'])
                            else:
                                pass 
                        elif gtr_data.split('_')[1]=='in':
                            res_data_mining=es_object.get_response_by_gtr_portfolio_report(index='instagram_profile_data_mining', gtr_id=data_each['GTR']) 
                            if res_data_mining:
                           
                                for data in res_data_mining:
                                    if data['algorithm_type']=='word_cloud':
                                        list_word_cloud.append(data['string_attributes'])
                                        if data['algorithm_type']=='common_words':
                                            list_common_words.append(data['list_attributes'])
                                        else:
                                            pass
                                    elif data['algorithm_type']=='common_words':
                                        list_common_words.append(data['list_attributes'])
                            else:
                                pass 
                        elif gtr_data.split('_')[1]=='rd':     
                            res_data_mining=es_object.get_response_by_gtr_portfolio_report(index='reddit_*_data_mining', gtr_id=data_each['GTR'])    
                            if res_data_mining:
                                for data in res_data_mining:
                                    if data['algorithm_type']=='word_cloud':
                                        list_word_cloud.append(data['string_attributes'])
                                        if data['algorithm_type']=='common_words':
                                            list_common_words.append(data['list_attributes'])
                                        else:
                                            pass

                                    elif data['algorithm_type']=='common_words':
                                        list_common_words.append(data['list_attributes'])
                            else:
                                pass
                        elif gtr_data.split('_')[1]=='sc':     
                            res_data_mining=es_object.get_response_by_gtr_portfolio_report(index='snapchat_*_data_mining', gtr_id=data_each['GTR'])    
                            if res_data_mining:
                                for data in res_data_mining:
                                    if data['algorithm_type']=='word_cloud':
                                        list_word_cloud.append(data['string_attributes'])
                                        if data['algorithm_type']=='common_words':
                                            list_common_words.append(data['list_attributes'])
                                        else:
                                            pass

                                    elif data['algorithm_type']=='common_words':
                                        list_common_words.append(data['list_attributes'])
                            else:
                                pass  
                        elif gtr_data.split('_')[1]=='tb':     
                            res_data_mining=es_object.get_response_by_gtr_portfolio_report(index='tumblr_*_data_mining', gtr_id=data_each['GTR'])    
                            if res_data_mining:
                                for data in res_data_mining:
                                    if data['algorithm_type']=='word_cloud':
                                        list_word_cloud.append(data['string_attributes'])
                                        if data['algorithm_type']=='common_words':
                                            list_common_words.append(data['list_attributes'])
                                        else:
                                            pass

                                    elif data['algorithm_type']=='common_words':
                                        list_common_words.append(data['list_attributes'])
                            else:
                                pass

                        elif gtr_data.split('_')[1]=='tk':     
                            res_data_mining=es_object.get_response_by_gtr_portfolio_report(index='tiktok_*_data_mining', gtr_id=data_each['GTR'])    
                            if res_data_mining:
                                for data in res_data_mining:
                                    if data['algorithm_type']=='word_cloud':
                                        list_word_cloud.append(data['string_attributes'])
                                        if data['algorithm_type']=='common_words':
                                            list_common_words.append(data['list_attributes'])
                                        else:
                                            pass

                                    elif data['algorithm_type']=='common_words':
                                        list_common_words.append(data['list_attributes'])
                            else:
                                pass    
                # final_list_common_word=   [{"count":each["count"],"tag":each["words"]} for each in itertools.chain(*list_common_words)]       
            

                final_list_common_word = []
                for each in itertools.chain(*list_common_words):
                    try:
                        # data = {"count":each["count"],"tag":each["words"]}
                        if "word" in each:

                            data = {"count":each["count"],"tag":each['word']}
                        else:
                            data = {"count":each["count"],"tag":each['hashtag']}
                        final_list_common_word.append(data)
                    except:
                        pass
                        # data = {"count":each["count"],"tag":each["hashtag"]}
                        # final_list_common_word.append(data)
                        

                # print(final_list_common_word)
                var=0
                for data in list_word_cloud:
                    if var==0:
                        string_word_cloud=data
                        var+=1
                    else:
                        string_word_cloud=string_word_cloud+' '+data
                        var+=1             
                new_list=(string_word_cloud.split(' '))
                set_list=set(new_list)
                dict_for_hashtag={make_keys:0 for make_keys in set_list}
                
                for  data_hashtags in new_list:
                    dict_for_hashtag[data_hashtags]=dict_for_hashtag[data_hashtags]+1
                    final_wordcloud_dict=[{'tag':key,"count":value} for key,value in dict_for_hashtag.items()]
                # print(final_wordcloud_dict)   
            except Exception as e:
                print(e)  
                     
            try:
                for data_each in portfolio_json_data_final['target']:
                    gtr_data=(data_each['GTR'])
                   
                    if gtr_data.split('_')[0]=='st':
                        if gtr_data.split('_')[1]=='fb':
                            res_list = es_object.get_response_by_gtr_portfolio_report(index='facebook_*_posts', gtr_id=data_each['GTR'])
                            # profile_information = es_object.get_response_by_gtr_portfolio_report(index='facebook_profile_profile_information', gtr_id=data_each['GTR'])
                            # result_data['profile_information'] = profile_information
                            if res_list :
                                date_list.append([each_date['created_on'] for each_date in res_list ])
                                try:
                                    prediction_list.append([each_date['categorization']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                try:
                                    sentiment_list.append([each_date['sentiment']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                try:
                                    emotion_list.append([each_date['emotion']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                
                                
                                result_data[data_each['GTR']]=(res_list)
                                 

                            

                            
                            else:
                                pass
                        
                    # profile_information 
                    #  'facebook_profile_profile_information'   
                        elif gtr_data.split('_')[1]=='tw':
                    
                            res_list = es_object.get_response_by_gtr_portfolio_report(index='twitter_*_posts', gtr_id=data_each['GTR'])
                            # profile_information = es_object.get_response_by_gtr_portfolio_report(index='twitter_profile_profile_information', gtr_id=data_each['GTR'])
                            # result_data['profile_information'] = profile_information
                            if res_list :
                                date_list.append([each_date['created_on'] for each_date in res_list ])
                                try:
                                    prediction_list.append([each_date['categorization']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                try:
                                    sentiment_list.append([each_date['sentiment']['predictions'] for each_date in res_list ])   
                                except:
                                    pass
                                try:
                                    emotion_list.append([each_date['emotion']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                result_data[data_each['GTR']]=(res_list)
                            else:
                               
                                pass    
                        elif gtr_data.split('_')[1]=='ln':
                            res_list = es_object.get_response_by_gtr_portfolio_report(index='linkedin_*_posts', gtr_id=data_each['GTR'])
                            # profile_information = es_object.get_response_by_gtr_portfolio_report(index='linkedin_profile_profile_information', gtr_id=data_each['GTR'])
                            # result_data['profile_information'] = profile_information
                            if res_list :
                                date_list.append([each_date['created_on'] for each_date in res_list ])
                                try:

                                    prediction_list.append([each_date['categorization']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                try:

                                    sentiment_list.append([each_date['sentiment']['predictions'] for each_date in res_list ]) 
                                except:
                                    pass
                                try:
                                    emotion_list.append([each_date['emotion']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                result_data[data_each['GTR']]=(res_list)
                            
                            else:
                                pass

                        elif gtr_data.split('_')[1]=='in':
                            res_list = es_object.get_response_by_gtr_portfolio_report(index='instagram_*_posts',gtr_id= data_each['GTR'])    
                            # profile_information = es_object.get_response_by_gtr_portfolio_report(index='instagram_profile_profile_information', gtr_id=data_each['GTR'])
                            # result_data['profile_information'] = profile_information
                            if res_list :
                                # print(res_list)
                                date_list.append([each_date['created_on'] for each_date in res_list ])
                                try:
                                    prediction_list.append([each_date['categorization']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                try:
                                    
                                    sentiment_list.append([each_date['sentiment']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                try:
                                    emotion_list.append([each_date['emotion']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                result_data[data_each['GTR']]=(res_list)
                            else:
                              
                                pass
                        elif gtr_data.split('_')[1]=='rd':
                            res_list = es_object.get_response_by_gtr_portfolio_report(index='reddit_*_posts',gtr_id= data_each['GTR'])    
                            # profile_information = es_object.get_response_by_gtr_portfolio_report(index='reddit_profile_profile_information', gtr_id=data_each['GTR'])
                            # result_data['profile_information'] = profile_information                            
                            if res_list :
                                date_list.append([each_date['created_on'] for each_date in res_list ])
                                try:

                                    prediction_list.append([each_date['categorization']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                try:
                                    sentiment_list.append([each_date['sentiment']['predictions'] for each_date in res_list ])  
                                except:
                                    pass
                                try:
                                    emotion_list.append([each_date['emotion']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                result_data[data_each['GTR']]=(res_list)
                            else:
                                print('no data')
                                pass     
                        elif gtr_data.split('_')[1]=='sc':
                            res_list = es_object.get_response_by_gtr_portfolio_report(index='snapchat_profile_stories',gtr_id= data_each['GTR'])    
                            # profile_information = es_object.get_response_by_gtr_portfolio_report(index='snapchat_profile_profile_information', gtr_id=data_each['GTR'])
                            # result_data['profile_information'] = profile_information                           
                            if res_list :
                                date_list.append([each_date['created_on'] for each_date in res_list ])
                                try:

                                    prediction_list.append([each_date['categorization']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                try:
                                    sentiment_list.append([each_date['sentiment']['predictions'] for each_date in res_list ])  
                                except:
                                    pass
                                try:
                                    emotion_list.append([each_date['emotion']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                result_data[data_each['GTR']]=(res_list)
                            else:
                                print('no data')
                                pass 
                        elif gtr_data.split('_')[1]=='tk':
                            res_list = es_object.get_response_by_gtr_portfolio_report(index='tiktok_profile_posts',gtr_id= data_each['GTR'])    
                            # profile_information = es_object.get_response_by_gtr_portfolio_report(index='tiktok_profile_profile_information', gtr_id=data_each['GTR'])
                            # result_data['profile_information'] = profile_information
                            if res_list :
                                date_list.append([each_date['created_on'] for each_date in res_list ])
                                try:

                                    prediction_list.append([each_date['categorization']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                try:
                                    sentiment_list.append([each_date['sentiment']['predictions'] for each_date in res_list ])  
                                except:
                                    pass
                                try:
                                    emotion_list.append([each_date['emotion']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                result_data[data_each['GTR']]=(res_list)
                            else:
                                print('no data')
                                pass    

                        elif gtr_data.split('_')[1]=='tb':
                            res_list = es_object.get_response_by_gtr_portfolio_report(index='tumblr_profile_posts',gtr_id= data_each['GTR'])    
                            # profile_information = es_object.get_response_by_gtr_portfolio_report(index='tumblr_profile_profile_information', gtr_id=data_each['GTR'])
                            # result_data['profile_information'] = profile_information
                            if res_list :
                                date_list.append([each_date['created_on'] for each_date in res_list ])
                                try:

                                    prediction_list.append([each_date['categorization']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                try:
                                    sentiment_list.append([each_date['sentiment']['predictions'] for each_date in res_list ])  
                                except:
                                    pass
                                try:
                                    emotion_list.append([each_date['emotion']['predictions'] for each_date in res_list ])
                                except:
                                    pass
                                result_data[data_each['GTR']]=(res_list)
                            else:
                                print('no data')
                                pass    
                    else:
                        pass                 
            except :
                pass
            # print('------------------------------__>emotion_list',emotion_list)
            emotion_final = []
            try:
                emotion_data=list(itertools.chain(*emotion_list[0]))
                dict_for_emotion={"worry":0,"neutral":0,"love":0,"sadness":0,"happiness":0}
                for  data_prediction in emotion_data:
                    dict_for_emotion[data_prediction]=dict_for_emotion[data_prediction]+1
                emotion_final=[{"prediction":prediction,"value":value} for prediction ,value  in dict_for_emotion.items() ]
            except Exception as e:
                print(e)
            sentiment_final = []
            try:
                sentiment_data=list(itertools.chain(*sentiment_list[0]))
                dict_for_sentiment={"Neutral":0,"Positive":0,"Negative":0}
                for  data_prediction in sentiment_data:
                    dict_for_sentiment[data_prediction]=dict_for_sentiment[data_prediction]+1
                sentiment_final=[{"prediction":prediction,"value":value} for prediction ,value  in dict_for_sentiment.items() ]
            except Exception as e:
                print(e)

            prediction_dict =[]
            try:
                prediction_data=list(itertools.chain(*prediction_list[0]))
                # dict_for_prediction={"blasphemy":0,"indecent":0,"law and order":0,"anti-state":0,"incitement  to offence":0,"pornographic":0,"contempt of court":0,"sectarian":0,"neither":0}
                # for  data_prediction in prediction_data:
                #     dict_for_prediction[data_prediction]=dict_for_prediction[data_prediction]+1
                dict_for_prediction = {}

                for data_prediction in prediction_data:
                    if data_prediction not in dict_for_prediction:
                        dict_for_prediction[data_prediction] = 1
                    else:
                        dict_for_prediction[data_prediction] = dict_for_prediction[data_prediction] + 1 
                prediction_dict=[{"prediction":prediction,"value":value} for prediction ,value  in dict_for_prediction.items() ]
            except :
                pass
            dict_portfolio_posts={}   
            try:
                date_of_posts=list(itertools.chain(*date_list))
                date_of_posts_converted=[datetime.datetime.fromtimestamp(data / 1e3) for data in date_of_posts ]
                dict_for_months={"Jan":0,"Feb":0,"Mar":0,"Apr":0,"May":0,"Jun":0,"Jul":0,"Aug":0,"Sep":0,"Oct":0,"Nov":0,"Dec":0}
                for dates in date_of_posts_converted:
                    datetime_object = datetime.datetime.strptime(str(dates.month), "%m")
                    month_name = datetime_object.strftime("%b")  
                    dict_for_months[month_name]=dict_for_months[month_name]+1
            except:
                pass 
            
            categorization_post_list = []
            categorization_count = {}
            if result_data:
                for gtr,posts in result_data.items():
                    for each_post in posts:
                        if "categorization" in each_post:
                            # print(each_post["categorization"]["predictions"])
                            predic_str = each_post['categorization']["predictions"][0]
                            categorization_post_list.append(predic_str)
                            if predic_str not in categorization_count:
                                categorization_count[predic_str] = 1
                            else:
                                categorization_count[predic_str] = categorization_count[predic_str] + 1

            post_categorization_count = [{"prediction":prediction,"value":value} for prediction ,value  in categorization_count.items() ]
                    


            dict_portfolio_posts['wordcloud']=final_wordcloud_dict         
            dict_portfolio_posts['hashtags']=final_hashtags_dict
            dict_portfolio_posts['mention']=final_mention_dict
            dict_portfolio_posts['common_word']=final_list_common_word    
            dict_portfolio_posts['phrases']=final_phrases_dict
            dict_portfolio_posts['keywords']=final_keyword_dict
            dict_portfolio_posts['emotions']=emotion_final
            dict_portfolio_posts['sentiment']=sentiment_final  
            # dict_portfolio_posts['categorization']=prediction_dict
            dict_portfolio_posts['categorization']=post_categorization_count
            dict_portfolio_posts['graph']=[{"months":key, "value":value} for key, value in dict_for_months.items()]
            dict_portfolio_posts['posts']=result_data
            dict_portfolio_posts['target']=target_list
            dict_portfolio_posts['categorization_post_list']=set(categorization_post_list)
            # dict_portfolio_posts['profile_information']=target_list
            portfolio_list.append(dict_portfolio_posts)
            new_list_case=[]
            new_list_keybase=[]
            new_list_target=[]
            for each_keybase in portfolio_json_data_final['keybase']:
                new_list_keybase.append(each_keybase)
            for each_case in portfolio_json_data_final['case']:
                new_list_case.append(each_case)   
            for each_target in portfolio_json_data_final['target']:
                new_list_target.append(each_target)      
            fake_list=[]
            count_intities=0
            count_posts=0
            for each_target in portfolio_json_data_final['linked_data']:
                fake_dict={}
                if each_target['type']=='fake_identity_generator':
                    print(each_target)
                    count_intities=count_intities+1
                    fake_dict['identity']=each_target
                elif each_target['type']=='ip_short' :
                    fake_dict['domain_ip_info']=each_target
                elif each_target['type']=='domain_ip_info' :
                    fake_dict['domain_info']=each_target
                elif each_target['type']=='domain_info' :
                    fake_dict['ip_short']=each_target
                elif each_target['type']=='google_scholar' :
                    fake_dict['google_scholar']=each_target
                elif each_target['type']=='google_patent' :
                    fake_dict['google_patent']=each_target
                elif each_target['type']=='dark_web' :
                    fake_dict['dark_web']=each_target   
                elif each_target['type']=='post_data' :
                    count_posts=count_posts+1
                    fake_dict['post_data']=each_target    
                elif each_target['type']=='twitter_searches' :
                    fake_dict['twitter_searches']=each_target      

                fake_list.append(fake_dict)
           
            # portfolio_dict['tools_details']=fake_list 
            portfolio_dict['total_intities']=count_intities 
            portfolio_dict['total_posts']=count_posts
            portfolio_dict['length_of_target']=len(new_list_target)  
            portfolio_dict['length_of_keybase']=len(new_list_keybase)     
            portfolio_dict['length_of_case']=len(new_list_case) 
            portfolio_list.append(portfolio_dict)
            



        except Exception as error:
            response={

                'message':str(error)

            }
            return Response(response)
            
        response={

                'message':portfolio_list

            }
        return Response(response)
        
class LinkedDataViewsets(viewsets.ModelViewSet):
    queryset = LinkedData.objects.all()
    permission_classes = (DjangoModelPermissions, IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return LinkedDataSerializer
        return LinkedDataSerializer

    def create(self, request, *args, **kwargs):
        data = perform_date_change(request.data)
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


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    permission_classes = (IsAuthenticated, DjangoModelPermissions)
    authentication_classes = (TokenAuthentication,)
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        print(self.request.version)
        if self.request.version == 'v1':
            return UserSerializer
        return UserSerializer
