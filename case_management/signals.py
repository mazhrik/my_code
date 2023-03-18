from django.db.models.signals import post_save, m2m_changed
from django.core import serializers
from case_management.serializers import CaseListSerializer
from django.dispatch import receiver
from .models import Case
import json
from OCS_Rest.settings import HDFS_ROOT_PATH
from core_management.hdfs_client import send_file
from core_management.elasticsearch_handler_v2 import ElasticsearchHandler

es_object = ElasticsearchHandler()
hdfs_app_directory = 'case_data'
elastic_index = 'case_management'


def perform(sender, instance, action):
    if action == "post_add" or action == "post_remove":
        case_number = instance.case_number
        file_name = "{0}.json".format(case_number)
        result = CaseListSerializer(
            instance=instance,
            many=False).data
        print("result", result)
        send_file(dir_to_store="{0}/{1}/".format(HDFS_ROOT_PATH, hdfs_app_directory), data_to_store=json.dumps(result),
                  case_name=file_name)
        es_object.save_document(index_string=elastic_index, unique_identity=instance.case_number,
                                json_file=json.dumps(result))
    else:
        pass


# receiver functions calls
@receiver(post_save, sender=Case, dispatch_uid='Create Case')
def create_social_target(sender, instance, created, **kwargs):
    print("After Creation of the social target")
    perform(sender, instance, "post_add")


@receiver(m2m_changed, sender=Case.locations.through)
def location_changed(sender, instance, action, **kwargs):
    perform(sender, instance, action)


@receiver(m2m_changed, sender=Case.investigators.through)
def investigator_changed(sender, instance, action, **kwargs):
    perform(sender, instance, action)


@receiver(m2m_changed, sender=Case.linked_data.through)
def linked_data_changed(sender, instance, action, **kwargs):
    perform(sender, instance, action)


@receiver(m2m_changed, sender=Case.evidences.through)
def evidences_changed(sender, instance, action, **kwargs):
    perform(sender, instance, action)


@receiver(m2m_changed, sender=Case.media.through)
def media_changed(sender, instance, action, **kwargs):
    perform(sender, instance, action)


@receiver(m2m_changed, sender=Case.people.through)
def person_added(sender, instance, action, **kwargs):
    perform(sender, instance, action)
