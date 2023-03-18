import datetime
from .ess_controller import EssApiController
from target_management.models import SocialTarget, GenericTarget, KeybaseTarget, UserNews
from core_management.constants import COUNTRY_LIST, CHANNEL_LIST, TWITTER_COUNTRIES, GOOGLE_COUNTRIES
from .signals import get_attribute

ess_object = EssApiController()


class PeriodicCall(object):

    def __init__(self):
        pass

    def invoke_target(self, instance, task_time):
        print("Invoked target")
        target_type = instance.GTR.split('_')[0]
        print(instance.GTR)
        print('Target_type', target_type)
        if target_type == 'st':
            print(target_type)
            updated = SocialTarget.update_ctr(obj=instance, ctr=instance.CTR, new_revoke=task_time)
            # instance = SocialTarget.objects.get(GTR=instance.GTR)
            if updated:
                print("Invoked Social target")
                if instance.CTR == 1:
                    pass
                else:
                    pass
                    # t_type, t_sub_type = get_attribute(instance.target_type, instance.target_sub_type)
                    # response = ess_object.add_target(username=instance.user_names, target_type=t_type,
                    #                                  target_sub_type=t_sub_type, GTR=instance.GTR,
                    #                                  CTR=instance.CTR, max_posts=instance.max_posts)
                    # print('Response1', response)
            else:
                print('Failed Update')
        elif target_type == 'dt':
            updated = GenericTarget.update_ctr(obj=instance, ctr=instance.CTR, new_revoke=task_time)
            # instance = GenericTarget.objects.get(GTR=instance.GTR)
            if updated:
                print("Invoked Generic target")
                if instance.CTR == 1:
                    pass
                else:
                    pass
                    # response = ess_object.dynamic_crawling(url=instance.url, ip_address=instance.ip,
                    #                                        domain=instance.domain,
                    #                                        pictures=instance.pictures, heading=instance.headings,
                    #                                        paragraphs=instance.paragraphs, links=instance.links,
                    #                                        videos=instance.videos, GTR=instance.GTR, CTR=instance.CTR)
                    # print('Response1', response)
            else:
                print('Failed Update')

        elif target_type == 'kb':
            updated = KeybaseTarget.update_ctr(obj=instance, ctr=instance.CTR, new_revoke=task_time)
            # instance = KeybaseTarget.objects.get(GTR=instance.GTR)
            if updated:
                print("Invoked Keybase target")
                if instance.CTR == 1:
                    pass
                else:
                    pass
                    # response = ess_object.add_keybase_target(keywords=instance.keybase.keywords,
                    #                                          social_sites=instance.site, GTR=instance.GTR,
                    #                                          CTR=instance.CTR)
                    # print('Response1', response)
            else:
                print('Failed Update')

    def add_target(self):
        social_objects = SocialTarget.objects.all()
        generic_objects = GenericTarget.objects.all()
        keybase_object = KeybaseTarget.objects.all()
        objects = list(social_objects) + list(generic_objects) + list(keybase_object)
        if objects:
            for obj in objects:
                target_type = obj.GTR.split('_')[0]
                print(obj.CTR)
                # print('Target_type', target_type)
                time_now = datetime.datetime.utcnow()
                # print('Time Now', time_now)
                invoke_time = obj.revoked_on
                # print('Time to invoke', invoke_time)
                if time_now > invoke_time and obj.is_enabled and obj.periodic_interval > 0:
                    task_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=obj.periodic_interval)
                    self.invoke_target(obj, task_time)
                    print("______________________________________task", task_time)
                    print("INVOKING")
                    print("______________________________________now", time_now)
                    print("############################################################################")

    def latest_trends(self):
        try:
            ess_object.youtube_trends()
            ess_object.reddit_trends()
            ess_object.twitter_trends(country='WORLD')

            for twitter_country in TWITTER_COUNTRIES:
                ess_object.twitter_trends(country=twitter_country)          

            for google_country in GOOGLE_COUNTRIES:
                ess_object.google_trends(country=google_country)
        except Exception as E:
            # print(E)
            pass

    def latest_news(self):
        try:
            channels = UserNews.objects.values_list("news_name", "channel_url").distinct()

            for channel in channels:
                ess_object.news_crawling(news_site=channel[0], top=30, channel_link=channel[1])

            # for channel in CHANNEL_LIST:
            #     ess_object.news_crawling(news_site=channel, top=30)

        except Exception as E:
            # print(E)
            pass
