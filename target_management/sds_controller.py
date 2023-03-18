import requests
from OCS_Rest import settings
import json

HEADERS = {
    'X-Requested-By': 'admin',
    'Content-Type': 'application/json',
}


class SDSController(object):
    def __init__(self):
        self.ip = settings.SDS_IP
        self.port = settings.SDS_PORT
        self.username = settings.SDS_USERNAME
        self.password = settings.SDS_PASSWORD
        self.base_url = settings.SDS_SERVER_BASE_URL
        self.token = ''
        self.header = ''

    def login(self):
        try:
            login_url = 'login'
            print(self.base_url + login_url)
            response = requests.post(self.base_url + login_url,
                                     json={'username': self.username, 'password': self.password})
            self.token = response.json()['access_token']

            self.header = {'Content-Type': 'application/json',
                           'Authorization': 'Bearer {0}'.format(self.token)}
            if response.status_code == 200:
                return True
            else:
                return False
            # if response.status_code == 200:
            #     print(self.header)
            #     self.ess_api_token = response.content.decode('utf-8').split(':')[1].strip('"}')
            #     print(self.ess_api_token)
            #     self.header = {'Content-Type': 'application/x-www-form-urlencoded',
            #                    'Authorization': 'Token {0}'.format(self.ess_api_token)}
            #
            #     print("Logged in")
            #     return True

        except Exception as e:
            # print(e)
            return False

    def do_request(self, payloads):
        self.login()
        url = self.base_url + 'sds'
        print(url)

        response = requests.post(url, headers=self.header, json=payloads)

        return response.json()

    def data_mining(self, task_type, task_subtype, gtr, ctr, target_type, target_subtype):
        try:
            paylaods = {'task_type': task_type, 'task_subtype': task_subtype, 'GTR': gtr, 'CTR': ctr,
                        'target_type': target_type, 'target_subtype': task_subtype}
            return self.do_request(paylaods)
        except Exception as error:
            return str(error)

    def analytics(self, task_type, task_subtype, gtr, ctr, target_type, target_subtype):
        try:
            paylaods = {'task_type': task_type, 'task_subtype': task_subtype, 'GTR': gtr, 'CTR': ctr,
                        'target_type': target_type, 'target_subtype': task_subtype}
            return self.do_request(paylaods)
        except Exception as error:
            return str(error)

    def text_processing(self, task_type, task_subtype, text, job_id, algorithim_type):
        try:
            paylaods = {'task_type': task_type, 'task_subtype': task_subtype, 'text': text, 'job_id': job_id,
                        'algorithim_type': algorithim_type}
            return self.do_request(paylaods)
        except Exception as error:
            return str(error)


# obj = SDSController()
#
# res = obj.text_processing('text_processing', 'common_words', 'Pakistan is a great country', 1, 'sentiment')
# print(res)
