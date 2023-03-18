import os
import sys

# from django.contrib.auth.models import User

# from account_management.models import AccountSettings
# from core_management.views import send_notification
# from target_management.models import SocialTarget
from django.contrib.auth.models import User

from account_management.models import AccountSettings
from core_management.views import send_notification
from target_management.models import SocialTarget

IN_CELERY_WORKER_PROCESS = sys.argv and sys.argv[0].endswith('celery') and 'worker' in sys.argv
IN_CELERY_BEAT_PROCESS = sys.argv and sys.argv[0].endswith('celery') and 'beat' in sys.argv
# from core_management.views import send_notification
# tm = Timeline_Manager()
# acq = Acquistion_Manager()

'''
code range 
OCS: 00-09
ESS: 10-19
MC: 20-29
HDFS: 30-39
NIFI: 40-49
BDS: 50-59
'''

SERVER_CODE = {"OCS": {'00': "Successful! target added", '01': 'Failed! target not added', '02':
    'Successful! target complete', '03': 'Failed! target not complete', '04': 'Successful!  AI job create',
                       '05': 'Failed!  AI job not created'},
               "ESS": {'10': 'API request received', '11': 'Invalid API request received',
                       '12': 'Task assign to micro-crawler', '13': 'Failed! Task not assign to MC'},
               "MC": {'20': 'API request received', '21': 'Failed! Invalid request', '22': 'Successful! Target queued',
                      '23': 'crawling Failed', '24': 'crawling complete',
                      '26': 'crawling complete', '28': 'media files Uploading Start',
                      '30': 'media files Uploading Complete', '25': 'media files Uploading Failed',
                      '27': 'Failed! data not store to BDS', '32': 'Successful! data store to BDS'},
               "BDS": {'40': 'Successful! Data received from MC', '41': 'Data Pattern Failed',
                       '32': 'Successful!  data processing start', '33': 'Successful!  data processing failed',
                       '42': 'Successful!  data processing start', '43': 'Successful!  data processing failed',
                       '50': 'Successful ! API request received', '51': 'Failed !  invalid task',
                       '52': 'Processing start', '54': 'Processing complete'}}


def on_messege_recived(data, **kwargs):
    server_name = data['server_name'].upper()
    print('-------------------------SERVER-----------', server_name)
    try:
        print("hi rabit ")
        print(data['message_type'], "gtr")
        if data['message_type'] == 'notification':
            print("inof noti")
            targets = SocialTarget.objects.get(GTR=data['arguments']['gtr'])
            print('targetsss 59', targets.user)
            print('targetsss 59', targets.user.id)
            user = User.objects.get(id=targets.user.id)
            user_settings = AccountSettings.objects.get(user=user)
            print("at line 60", user_settings.OCS)
            print(int(data['arguments']['status']) % 2, 'status code')
            if int(data['arguments']['status']) % 2 == 0 and user_settings.OCS == 'success':
                send_notification(user=user.id, messege=data['messege'] + targets.user_names)
                print("if ss")
            elif int(data['arguments']['status']) % 2 != 0 and user_settings.OCS == 'fail':
                send_notification(user=user.id, messege=data['messege'] + targets.user_names)
                print("eliffff")

            elif user_settings.OCS == 'both':
                send_notification(user=user.id, messege=data['messege'] + targets.user_names)
                print("both")
            else:
                print("process done no option is selected yet")
        print('-----------------------------STATUS-----------------------')
    except Exception as error:
        print('----------------------', error, '-------------------------')
        pass
    try:
        print('-----------------------------', SERVER_CODE['server_name'], '----------------------------')
    except Exception as error:
        pass
