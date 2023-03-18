import json
from datetime import datetime
from cryptography.fernet import Fernet
from django.contrib.auth.models import User
from django.db.models import Q

from case_management.models import Case
from keybase_management.models import Keybase
from portfolio_management.models import Individual, Group, Event
from target_management.models import SocialTarget, Target, GenericTarget


class TargetData_Handler:
    """
    will return the counts of targets
    """
    fernet = None
    deycrypted_data = None
    target_counts = None
    jsondata = None

    def __init__(self):
        with open('key.key', 'rb') as f:
            self.key = f.read()
        f.close()
        with open('secretfile.crt', 'rb') as file:
            self.data = file.read()
        self.fernet = Fernet(self.key)
        self.deycrypted_data = self.fernet.decrypt(self.data)
        self.target_counts = self.deycrypted_data.decode('utf-8')
        self.jsondata = json.loads(self.target_counts)
        print(self.jsondata)

    def social_media_total_target_count(self):
        """
        return the total social media's count
        """

        social_total_target = SocialTarget.objects.filter(
            Q(created_on__icontains=datetime.date(datetime.now()))).count()
        context = {"social_media_total_target_count":
                       self.jsondata['Target_count'][0]['Social_media_target'][0]['total_social_media_target_count'],
                   "total_db_count": social_total_target}

        return context

    def facebook_target_count(self):
        """
        return the total facebook Count
        """
        social_total_target = SocialTarget.objects.filter(
            Q(created_on__icontains=datetime.date(datetime.now())) & Q(target_type='fb')).count()
        context = {"facebook_target_count":
                       self.jsondata['Target_count'][0]['Social_media_target'][0]['facebook_target_count'],
                   "total_db_count": social_total_target}
        if context['total_db_count'] >= context['facebook_target_count']:
            return False
        else:
            return True

    def instagram_target_count(self):
        """
        return the total Instagram Count
        """
        social_total_target = SocialTarget.objects.filter(
            Q(created_on__icontains=datetime.date(datetime.now())) & Q(target_type='in')).count()
        context = {
            "instagram_target_count":
                self.jsondata['Target_count'][0]['Social_media_target'][0]['Insta_target_count'],
            "total_db_count": social_total_target
        }
        if context['total_db_count'] >= context['instagram_target_count']:
            return False
        else:
            return True

    def twitter_target_count(self):
        """
        return the total Twitter Count
        """
        social_total_target = SocialTarget.objects.filter(
            Q(created_on__icontains=datetime.date(datetime.now())) & Q(target_type='tw')).count()
        context = {
            "Twitter_target_count":
                self.jsondata['Target_count'][0]['Social_media_target'][0]['Twitter_target_count'],
            "total_db_count": social_total_target
        }
        if context['total_db_count'] >= context['Twitter_target_count']:
            return False
        else:
            return True

    def reddit_target_count(self):
        """
         return the total Reddit Count
        """
        social_total_target = SocialTarget.objects.filter(
            Q(created_on__icontains=datetime.date(datetime.now())) & Q(target_type='rd')).count()
        context = {
            "Reddit_target_count":
                self.jsondata['Target_count'][0]['Social_media_target'][0]['Reddit_target_count'],
            "total_db_count": social_total_target
        }
        if context['total_db_count'] >= context['Reddit_target_count']:
            return False
        else:
            return True

    def total_target_count(self):
        """
        return the total target Count
        """
        social_total_target = Target.objects.filter(Q(created_on__icontains=datetime.date(datetime.now()))).count()
        context = {
            "total_target_count":
                self.jsondata['Target_count'][0]['total_target_count'],
            "total_db_count": social_total_target
        }
        if context['total_db_count'] >= context['total_target_count']:
            return False
        else:
            return True

    def generic_crawler(self):
        """
        return the total generic_crawler Count
        """
        social_total_target = GenericTarget.objects.filter(
            Q(created_on__icontains=datetime.date(datetime.now())) & Q(target_type='gn')).count()
        context = {
            "generic_crawler_count":
                self.jsondata['Target_count'][0]['generic_crawler'][0]['total_generic_count'],
            "total_db_count": social_total_target
        }
        if context['total_db_count'] >= context['generic_crawler_count']:
            return False
        else:
            return True

    def keybase_target(self):
        """
        return the total keybase_target Count
        """
        social_total_target = Keybase.objects.filter(
            Q(created_on__icontains=datetime.date(datetime.now())) & Q(target_type='kb')).count()
        context = {
            "keybase_target":
                self.jsondata['Target_count'][0]['keybase_target'][0]['total_keybase_target_count'],
            "total_db_count": social_total_target
        }
        if context['total_db_count'] >= context['keybase_target']:
            return False
        else:
            return True

    def linkedin_target(self):
        """
        return the total LinkedIn Count
        """
        social_total_target = SocialTarget.objects.filter(
            Q(created_on__icontains=datetime.date(datetime.now())) & Q(target_type='in')).count()
        context = {
            "linkedin_target_count":
                self.jsondata['Target_count'][0]['Social_media_target'][0]['linkedin_target_count'],
            "total_db_count": social_total_target
        }
        if context['total_db_count'] >= context['linkedin_target_count']:
            return False
        else:
            return True

    def user_accounts(self):
        """
        return the total added User Count
        """
        social_total_target = User.objects.all().count()
        context = {
            "useraccounts":
                self.jsondata['Target_count'][0]['Account_count'][0]['total_account_count'],
            "total_db_count": social_total_target
        }
        if context['total_db_count'] >= context['useraccounts']:
            return False
        else:
            return True

    def indiviual_portfolio_count(self):
        """
        return the Indiviual portfolio User Count
        """
        social_total_target = Individual.objects.filter(
            Q(created_on__icontains=datetime.date(datetime.now())) & Q(target_type='in')).count()
        context = {
            "individual_portfolio":
                self.jsondata['Target_count'][0]['Portfolio_count'][0]['individual_portfolio'],
            "total_db_count": social_total_target
        }
        if context['total_db_count'] >= context['useraccounts']:
            return False
        else:
            return True

    def group_portfolio_count(self):
        """
        return the group Count
        """
        social_total_target = Group.objects.filter(
            Q(created_on__icontains=datetime.date(datetime.now()))).count()
        context = {
            "group_portfolio":
                self.jsondata['Target_count'][0]['Portfolio_count'][0]['group_portfolio'],
            "total_db_count": social_total_target
        }
        if context['total_db_count'] >= context['group_portfolio']:
            return False
        else:
            return True

    def Event_portfolio_count(self):
        """
        return the event Count
        """
        social_total_target = Event.objects.filter(
            Q(created_on__icontains=datetime.date(datetime.now()))).count()
        context = {
            "group_portfolio":
                self.jsondata['Target_count'][0]['Portfolio_count'][0]['group_portfolio'],
            "total_db_count": social_total_target
        }
        if context['total_db_count'] >= context['group_portfolio']:
            return False
        else:
            return True

    def Case_count(self):
        """
        return the total added User Count
        """
        social_total_target = Case.objects.filter(
            Q(created_on__icontains=datetime.date(datetime.now()))).count()
        context = {
            "Case_count":
                self.jsondata['Target_count'][0]['Case_count'][0]['total_case_target_count'],
            "total_db_count": social_total_target
        }
        if context['total_db_count'] >= context['Case_count']:
            return False
        else:
            return True


def limit_check(target_type):
    """
    checks the limit of the models

    @params <required>
    """
    target = target_type
    handle = TargetData_Handler()
    print("tagaggaga")
    if target == 'fb':
        print(target, "is data")
        data = handle.facebook_target_count()
        print(data, "is data")
        return data
    elif target == 'in':
        print(target, "is data")
        data = handle.instagram_target_count()
        print(data, "is data")
        return data
    elif target == 'tw':
        print(target, "is data")
        data = handle.twitter_target_count()
        print(data, "is data")
        return data
    elif target == 'rd':
        print(target, "is data")
        data = handle.reddit_target_count()
        print(data, "is data")
        return data
    elif target == 'ln':
        print(target, "is data")
        data = handle.linkedin_target()
        print(data, "is data")
        return data
    elif target == 'gn':
        print(target, "is data")
        data = handle.generic_crawler()
        print(data, "is data")
        return data
    elif target == 'kb':
        print(target, "is data")
        data = handle.keybase_target()
        print(data, "is data")
        return data
    elif target is "account":
        print("function called")
        data = handle.user_accounts()
        print("data", data)
        return data
    elif target == 'case':
        data = handle.Case_count()
        return data
    elif target == 'ind':
        data = handle.indiviual_portfolio_count()
        return data
    elif target == 'group':
        data = handle.group_portfolio_count()
        return data
    elif target == 'event':
        data = handle.Event_portfolio_count()
        return data
#
# # def model_decorator(func):
# #     def wrapper(classname, *args, **kwargs):
# #         print('args - ', args)
# #         print('kwargs - ', kwargs)
# #         # print('class - ', classname.__class__().a())
# #         print('class - ', classname.__class__.__name__)
# #         obj = classname.__class__.__name__
# #         handler = TargetData_Handler()
# #         if obj == "portfolio":
# #             print("hi")
# #             return "good"
# #         elif obj == "SocialTarget" and kwargs['target_type'] == 'fb':
# #             data = handler.facebook_target_count()
# #             print(data)
# #             if data['total_db_count'] >= data['facebook_target_count']:
# #                 print("hi hamza")
# #             else:
# #                 print("doneeee , doneeee")
# #                 classname.__class__().save()
# #
# #         elif obj == "SocialTarget" and kwargs['target_type'] == 'in':
# #             data = handler.facebook_target_count()
# #             print(data)
# #             if data['total_db_count'] >= data['facebook_target_count']:
# #                 print("hi hamza")
# #             else:
# #                 print("doneeee , doneeee")
# #                 classname.__class__().a()
# #                 return func(classname, *args, **kwargs)
# #         elif obj == "SocialTarget" and kwargs['target_type'] == 'tw':
# #             data = handler.facebook_target_count()
# #             print(data)
# #             if data['total_db_count'] >= data['facebook_target_count']:
# #                 print("hi hamza")
# #             else:
# #                 print("doneeee , doneeee")
# #                 # classname.__class__().a()
# #                 return func(classname, *args, **kwargs)
# #
# #         elif obj == "SocialTarget" and kwargs['target_type'] == 'ln':
# #             data = handler.facebook_target_count()
# #             print(data)
# #             if data['total_db_count'] >= data['facebook_target_count']:
# #                 print("hi hamza")
# #             else:
# #                 print("doneeee , doneeee")
# #                 # classname.__class__().a()
# #                 return func(classname, *args, **kwargs)
# #
# #         elif obj == "GenericTarget":
# #             data = handler.facebook_target_count()
# #             print(data)
# #             if data['total_db_count'] >= data['facebook_target_count']:
# #                 print("hi hamza")
# #             else:
# #                 print("doneeee , doneeee")
# #                 # classname.__class__().a()
# #                 return func(classname, *args, **kwargs)
# #         elif obj == "GenericTarget":
# #             data = handler.facebook_target_count()
# #             print(data)
# #             if data['total_db_count'] >= data['facebook_target_count']:
# #
# #                 print("hi hamza")
# #             else:
# #                 print("doneeee , doneeee")
# #                 classname.__class__().save()
# #         else:
# #             print("failed")
# #     return wrapper


# from cryptography.fernet import Fernet
#
# # this generates a key and opens a file 'key.key' and writes the key there
# key = Fernet.generate_key()
# file = open('key.key', 'wb')
# file.write(key)
# file.close()
#
# # this just opens your 'key.key' and assings the key stored there as 'key'
# # file = open('key.key', 'rb')
# # key = file.read()
# # file.close()
#
# # this opens your json and reads its data into a new variable called 'data'
# # with open('/home/ameer/Target_count.json', 'rb') as f:
# with open('/home/ameer/Target_counts.json', 'rb') as f:
#     data = f.read()
# print(data)
# # this encrypts the data read from your json and stores it in 'encrypted'
# fernet = Fernet(key)
# encrypted = fernet.encrypt(data)
# # deyc = fernet.decrypt(data)
# # print(deyc)
# #
# # this writes your new, encrypted data into a new JSON file
# with open('secretfile.crt', 'wb') as f:
#     f.write(encrypted)
