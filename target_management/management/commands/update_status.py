from django.core.management.base import BaseCommand
from target_management.models import SocialTarget, KeybaseTarget, GenericTarget
from django.utils import timezone
from target_management.constants import SERVER_CODE, NEW_SERVER_CODE, target_status_dic,auto_update_status_dic
from target_management.views import translate_status_from_json_status_code

class Command(BaseCommand):
    help = 'Displays current time'

    def handle(self, *args, **kwargs):
        time = timezone.now().strftime('%X')

        
        def update_all(all_target_object):
            for target_object in all_target_object:
                # print(target_object.target_status_string)
                list_of_status = target_object.target_status_string.split(',')
                server = dict(SERVER_CODE)
                new_server = {}
                for key, value in server.items():
                    new_server[value]=key
                dic_ = target_object.target_status_dic

                for each_status in list_of_status:
                    if each_status in new_server:
                        target_status = new_server[each_status]
                        if str(target_status) in target_status_dic:
                            if str(target_status) == "24":
                                for key , value in dic_.items():
                                    if value['message'] != 'Target Marked':
                                        value['time'] = ""
                            if str(target_status) == "32" or str(target_status) == "30" or str(target_status) == "28" :
                                if "3" in dic_:
                                    if dic_["3"]['message'] == "Crawling Failed":
                                        dic_["3"]['message'] = "Crawling Completed"
                            if target_status_dic[str(target_status)] not in dic_:
                                new_auto_update_status_dic = {value:key for key, value in auto_update_status_dic.items()}
                                dic_[target_status_dic[str(target_status)]] =  {"message": translate_status_from_json_status_code(status_code=target_status), "time":str(time), "server_request":True} 
                                for each_key in range(int(target_status_dic[str(target_status)]),0,-1):
                                    if str(each_key) not in dic_:
                                        dumping_target_status =new_auto_update_status_dic[str(each_key)]
                                        dic_[target_status_dic[str(dumping_target_status)]] =  {"message": translate_status_from_json_status_code(status_code=dumping_target_status), "time":str(time) ,"server_request":False  } 
                                        
                                target_object.update()
                                print(" --------------- {0} --------------------".format(target_object.GTR))
        all_target_object = SocialTarget.objects.all()
        update_all(all_target_object)
        all_target_object = KeybaseTarget.objects.all()
        update_all(all_target_object)
        all_target_object = GenericTarget.objects.all()
        update_all(all_target_object)
        # for each_st in st:
        #     print(each_st.target_status_string)

        self.stdout.write("It's now %s" % time)