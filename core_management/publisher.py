import pika
import pika.exceptions
import datetime
import json
from OCS_Rest.settings import HOST_CONSUMER, PASSWORD_CONSUMER, USERNAME_CONSUMER
import sys
import requests
#
# SERVER_NAME = "ESS"
# USERNAME = "ess"
# PASSWORD = "rapidev"
# exchange = "control_exchange"
# # OCS_IP = "192.168.18.175"
# # OCS_PORT = 8000
# # OCS_USERNAME = "saad"
# # OCS_PASSWORD = "12345678"


class Rabbit_Publisher(object):
    """
    Class to create the publisher object and use it to broadcast the messages to all listners
    it also consists all the class level variables
    """

    # class level variables bellow

    HOST = HOST_CONSUMER
    USERNAME = USERNAME_CONSUMER
    PASSWORD = PASSWORD_CONSUMER
    EXCHANGE = None
    EXCHANGE_TYPE = 'topic'
    ROUTING_KEY = ''
    PROPERTIES = pika.BasicProperties(content_type='application/json', delivery_mode=1)
    VIRTUAL_HOST = 'new_system_control'

    def __init__(self, host=HOST, username=USERNAME, password=PASSWORD, exchange='new_control_exchange'):
        """
        Do initial connection to the rabbitmq server and create a queue
        """

        self.HOST = host
        self.USERNAME = username
        self.PASSWORD = password
        self.EXCHANGE = exchange
        self._connection = None
        try:
            credentials = pika.credentials.PlainCredentials(self.USERNAME, self.PASSWORD)
            self._connection =pika.BlockingConnection(pika.ConnectionParameters(host=self.HOST, credentials=credentials,
                                                                                virtual_host=self.VIRTUAL_HOST))
            if(self._connection.is_open):
                self._connection.add_on_connection_blocked_callback(self.on_connection_blocked)
                self._connection.add_on_connection_unblocked_callback(self.on_connection_open_unblocked)
                self._connection.add_callback_threadsafe(self.blocking_thread)
                self.channel = self._connection.channel()
                self.channel.exchange_declare(exchange=self.EXCHANGE, exchange_type=self.EXCHANGE_TYPE,
                                              durable=True, auto_delete=True)
                self.channel.confirm_delivery()
                print('....................RabbitMq Connected To Exchange : {0}..............'.format(self.EXCHANGE))
        except pika.exceptions.ProbableAuthenticationError as e:
            print('.....................................RabbitMq Not Connected........................................')
            print(e)
        except Exception as e:
            print(e)

    def on_connection_blocked(self):
        print('................................Connection Blocked By RabbitMq..............................')

    def on_delivery_confirmation(self, method_frame):

        confirmation_type = method_frame.method.NAME.split('.')[1].lower()
        print(method_frame)

    def on_connection_open_unblocked(self):
        print('................................Connection Un-Blocked By RabbitMq..............................')

    def blocking_thread(self):
        print('................................In Blocking Connection Safe Thread..............................')

    def is_connected(self):
        if(self._connection is not None):
            return self._connection.is_open
        return False

    def publish(self, message, routing_key='',):
        print("message------------->",message)
        try:
            if(self.is_connected()):
                val = self.channel.basic_publish(exchange=self.EXCHANGE,
                                                 routing_key=self.ROUTING_KEY,
                                                 body=json.dumps(message),
                                                 properties=self.PROPERTIES,
                                                 mandatory=True
                                                 )
                # print(self.channel.basic_get(self.EXCHANGE))
                return True

        except pika.exceptions.UnroutableError as e:
            print('Message is returned, it says ', e)

        except pika.exceptions.ChannelClosed as e:
            print(e)
        except pika.exceptions.ConnectionClosed as e:
            print(e)
        except pika.exceptions.ConnectionOpenAborted as e:
            print(e)
        except pika.exceptions.ChannelError as e:
            print(e)

        except Exception as e:
            print(e)

        return False


def publish(message, module_name=__name__, message_type='info', **kwargs):
    if kwargs["code"] and kwargs["GTR"]:
        update_status(kwargs["code"], kwargs["GTR"])
    pub = Rabbit_Publisher(username=USERNAME, password=PASSWORD, exchange=exchange)
    # publish({'server_name': 'OCS', 'module_name': __name__, 'messege_type': 'info','arguments':{'name':'awais'},
    # 'messege':'this is the messege'})
    pub.publish({'server_name': SERVER_NAME, 'module_name': module_name,
                 'message_type': message_type,
                 'arguments': kwargs,
                 'messege': message})


def login(username, password):
    payload = {"username": username, "password": password}
    response = requests.post(f"http://{OCS_IP}:{OCS_PORT}/v1/account/login/", data=payload)
    response = response.json()
    return response["result"]["token"]


def update_status(status_code, GTR):
    token = login(OCS_USERNAME, OCS_PASSWORD)
    payload = {"target_status": status_code, "GTR": GTR}
    headers = {'Authorization': f'Token {token}'}
    response = requests.post(f"http://{OCS_IP}:{OCS_PORT}/v1/target/updatestatus/", data=payload, headers=headers)
    print(response.json())


# 192.168.18.175:8000/v1/account/login/
# def publish_control(message,module_name = __name__):
# publish({'server_name': SERVER_NAME, 'module_name': module_name, 'messege_type': 'control','arguments':{},
# 'messege':message})


# if __name__ == '__main__':
#    pub = Rabbit_Publisher(username='ocs',password='rapidev',exchange='control_exchange')
#    data = {'server_name':'OCS','node_id':1,'messege_type':'control, awais'}
#    print(pub.publish(data))

# !/usr/bin/env python
# import pika
# import pika.exceptions
# import datetime
# import json
# import sys

# class Rabbit_Publisher(object):

#     """
#     Class to create the publisher object and use it to broadcast the messages to all listners
#     it also consists all the class level variables
#     """

#     #class level variables bellow

#     HOST = None
#     USERNAME = None
#     PASSWORD = None
#     EXCHANGE = None
#     EXCHANGE_TYPE = 'fanout'
#     ROUTING_KEY = ''
#     PROPERTIES = pika.BasicProperties(content_type='application/json',delivery_mode=1)
#     VIRTUAL_HOST = 'system_control'


#     def __init__(self,host = '192.168.18.27',username = '',password = '',exchange=''):
#         """
#         Do initial connection to the rabbitmq server and create a queue
#         """

#         self.HOST = host
#         self.USERNAME = username
#         self.PASSWORD = password
#         self.EXCHANGE = exchange
#         self._connection = None
#         try:
#             credentials = pika.credentials.PlainCredentials(self.USERNAME, self.PASSWORD)
#             self._connection =pika.BlockingConnection(pika.ConnectionParameters(host=self.HOST,
#             credentials=credentials,virtual_host=self.VIRTUAL_HOST))
#             if(self._connection.is_open):
#                 self._connection.add_on_connection_blocked_callback(self.on_connection_blocked)
#                 self._connection.add_on_connection_unblocked_callback(self.on_connection_open_unblocked)
#                 self._connection.add_callback_threadsafe(self.blocking_thread)
#                 self.channel = self._connection.channel()
#                 self.channel.exchange_declare(exchange=self.EXCHANGE, exchange_type=self.EXCHANGE_TYPE,
#                 durable=False, auto_delete=False)
#                 self.channel.confirm_delivery()
#                 print('.....................................RabbitMq Connected To Exchange :
#                 {0}.......................'.format(self.EXCHANGE))
#         except pika.exceptions.ProbableAuthenticationError as e :
#             print('..................................RabbitMq Not Connected.....................................')
#             print(e)
#         except Exception as e:
#             print(e)

#     def on_connection_blocked(self):
#         print('................................Connection Blocked By RabbitMq..............................')

#     def on_delivery_confirmation(self, method_frame):

#         confirmation_type = method_frame.method.NAME.split('.')[1].lower()
#         print(method_frame)

#     def on_connection_open_unblocked(self):
#         print('................................Connection Un-Blocked By RabbitMq..............................')

#     def blocking_thread(self):
#         print('................................In Blocking Connection Safe Thread..............................')

#     def is_connected(self):
#         if(self._connection is not None):
#             return self._connection.is_open
#         return False

#     def publish(self,message,routing_key = '',):
#         try:
#             if(self.is_connected()):
#                 val = self.channel.basic_publish(exchange=self.EXCHANGE,
#                                       routing_key=self.ROUTING_KEY,
#                                       body=json.dumps(message),
#                                       properties=self.PROPERTIES,
#                                       mandatory=True
#                                            )
#                 #print(self.channel.basic_get(self.EXCHANGE))
#                 return True

#         except pika.exceptions.UnroutableError as e:
#             print('Message is returned, it says ', e)

#         except pika.exceptions.ChannelClosed as e:
#             print(e)
#         except pika.exceptions.ConnectionClosed as e:
#             print(e)
#         except pika.exceptions.ConnectionOpenAborted as e:
#             print(e)
#         except pika.exceptions.ChannelError as e:
#             print(e)

#         except Exception as e:
#             print(e)

#         return False
