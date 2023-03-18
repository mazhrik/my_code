from rest_framework import viewsets
from core_management.elasticsearch_handler import ElasticsearchHandler
from django.http import JsonResponse

# Create your views here.


elasticsearch_obj = ElasticsearchHandler()


class BiTools(viewsets.ViewSet):

    def list(self, request):

        main_list = []
        main_dict = {}
        count = 0
        # if request.data is not None:
        #     index = request.data['index']
        #     query_type = request.data['query_type']
        #     attribute = request.data['attribute']
        #     query_value = request.data['query_value']
        #     logical_operator = request.data['logical_operator']
        #
        #     print(index, query_type, attribute, query_value, logical_operator)

        responses = elasticsearch_obj.bi_tool_matched_query_result('twitter_profile_response_tms',
                                                                   'profile_information',
                                                                   ['username', 'user_id', 'name'],
                                                                   ['UKMoments', 2296297326,
                                                                    'Twitter Moments UK & Ireland'], ['and', 'or'])

        for response in responses['hits']['hits']:
            main_list.append(response['_source'])

        for data in main_list:
            main_dict[count] = data
            count += 1

        # response_serialized = serializers.serialize('json', main_dict)
        return JsonResponse(main_dict, safe=False)

        #
        #
        # response = {
        #     'message': 'Values Get successfully',
        #     'status': True,
        #     'error': None
        # }
        # return JsonResponse(json.dumps(main_dict))
