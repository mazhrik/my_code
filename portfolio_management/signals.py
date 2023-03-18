from django.db.models.signals import post_save, m2m_changed
from django.core import serializers
from case_management.serializers import CaseListSerializer
from django.dispatch import receiver
from .models import Case
import json
from OCS_Rest.settings import HDFS_ROOT_PATH
from core_management.hdfs_client import send_file
from portfolio_management.serializers import EventSerializerV1, IndividualSerializerV1, GroupSerializerV1
from core_management.elasticsearch_handler_v2 import ElasticsearchHandler
from portfolio_management.models import Individual, Event, Group


es_object = ElasticsearchHandler()
hdfs_app_directory = 'case_data'
elastic_index = 'portfolio_management_group'


def perform(sender, instance, action):
    if action == "post_add" or action == "post_remove":
        event_obj = Group.objects.all()
        # case_number = instance.case_number
        # file_name = "{0}.json".format(case_number)
        # result = CaseListSerializer(
        #     instance=instance,
        #     many=False).data
        # print("result", result)
        data = GroupSerializerV1(Group.objects.get(id=23)).data
        print(data)
        for i in event_obj:

            es_object.save_document(index_string=elastic_index, unique_identity=i.id,
                                    json_file=json.dumps(data))
    else:
        pass


