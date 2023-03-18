from django.db.models.signals import post_save
from django.dispatch import receiver
from django.http import request
from .models import SocialTarget, GenericTarget, KeybaseTarget
from target_management import ess_controller
from .constants import *
import itertools
import json

ess_object = ess_controller.EssApiController()


# receiver functions calls
def get_attribute(target_type, sub_target_type):
    translate_target = dict(TARGET_TYPE)
    translate_subtarget = dict(TARGET_SUB_TYPE)
    target_type_translated = translate_target[str(target_type)]
    target_sub_type_translated = translate_subtarget[str(sub_target_type)]
    return target_type_translated, target_sub_type_translated


def get_attribute_keybase(target_type):
    translate_target = dict(TARGET_TYPE)
    target_type_translated = translate_target[str(target_type)]
    return target_type_translated


def convert_sites_dict(input_dict):
    sites_array = input_dict.split(',')
    output_dict = {}
    all_keys = {"fb", "instagram", "twitter", "youtube", "reddit", "linkedin", "search_engine", "news", "darkweb"}
    for site in sites_array:
        if site == 'fb':
            translated_site_name = {site: True}
        else:
            site_type = get_attribute_keybase(site)
            translated_site_name = {site_type: True}
        output_dict.update(translated_site_name)
    false_fields = all_keys - {*output_dict}
    for key in false_fields:
        false_dict = {key: False}
        output_dict.update(false_dict)
    print('actual', output_dict)
    return output_dict


@receiver(post_save, sender=SocialTarget, dispatch_uid='Create Social Target')
def create_social_target(sender, instance, created, **kwargs):
    print("After Creation of the social target")
    if created:
        if ess_object.connect():
            target_type, sub_type = get_attribute(target_type=instance.target_type,
                                                  sub_target_type=instance.target_sub_type)
            response = ess_object.add_target(username=instance.user_names, target_type=target_type,
                                             target_sub_type=sub_type, GTR=instance.GTR,
                                             CTR=instance.CTR, max_posts=instance.max_posts, avatar_password=instance.avatar_password, 
                                             avatar_username=instance.avatar_username)
            print(response)
        else:
            pass


# receiver functions calls
@receiver(post_save, sender=GenericTarget,
          dispatch_uid='Create Generic Target')
def create_generic_target(sender, instance, created, **kwargs):
    print("After Creation of the generic target")
    if created:
        if ess_object.connect():
            response = ess_object.dynamic_crawling(url=instance.url, ip_address=instance.ip, domain=instance.domain,
                                                   pictures=instance.pictures, heading=instance.headings,
                                                   paragraphs=instance.paragraphs, links=instance.links,
                                                   videos=instance.videos, GTR=instance.GTR, CTR=instance.CTR, vpn=instance.vpn)
            print(response)
        else:
            pass


# receiver functions calls
@receiver(post_save,
          sender=KeybaseTarget,
          dispatch_uid='Create Keybase Target')
def create_keybase_target(sender, instance, created, **kwargs):
    print("After Creation of the generic target")
    if created:
        final_payloads = []
        keywords = {}
        final_payloads = instance.keybase.keywords + instance.keybase.hashtags + instance.keybase.phrases + instance.keybase.mentions
        duplicates_removed = set(final_payloads)
        final_list = list(duplicates_removed)
        if ess_object.connect():
            sites_dict = convert_sites_dict(instance.site)
            response = ess_object.add_keybase_target(keywords=final_list,
                                                     social_sites=sites_dict, GTR=instance.GTR, CTR=instance.CTR)
            print(response)
        else:
            pass
