import json
import threading
from socketIO_client import SocketIO, LoggingNamespace, BaseNamespace
from OCS_Rest import settings


def on_connect():
    print("I'm connected to the server")
    
def connect_error():
    print('[INFO] Failed to connect to server.')



def disconnect():
    print('[INFO] Disconnected from server.')


def user_disconnected(data):
    print("this is disconnected")

        

def facebook_message(data):
    print('I received a message!')
    with open('{}_data.json'.format("facebook"),'w') as f:
        json.dump(data,f,indent=4)

        

def twitter_message(data):
    print('I received a message!')
    with open('{}_data.json'.format("twitter"),'w') as f:
        json.dump(data,f,indent=4)
        

def instagram_message(data):
    print('I received a message!')
    with open('{}_data.json'.format("instagram"),'w') as f:
        json.dump(data,f,indent=4)


def reddit_message(data):
    print('I received a message!')
    with open('{}_data.json'.format("reddit"),'w') as f:
        json.dump(data,f,indent=4)
        

def youtube_message(data):
    print('I received a message!')
    with open('{}_data.json'.format("youtube"),'w') as f:
        json.dump(data,f,indent=4)
        

def linkedin_message(data):
    print('I received a message!')
    with open('{}_data.json'.format("linkedin"),'w') as f:
        json.dump(data,f,indent=4)
        

def tiktok_message(data):
    print('I received a message!')
    with open('{}_data.json'.format("tiktok"),'w') as f:
        json.dump(data,f,indent=4)

def tumblr_message(data):
    print('I received a message!')
    with open('{}_data.json'.format("tumblr"),'w') as f:
        json.dump(data,f,indent=4)
                    
def image_reverse_lookup_message(data):
    print('I received a message!')
    print(data)
    with open('{}_data.json'.format("image_reverse_lookup"),'w') as f:
        json.dump(data,f,indent=4)

import uuid
class TargetIdentifySocialMedia():
    def __init__(self):
        self.target_data = [] 
        
    def message1(self):
        print("crawled")

    
    def message2(self):
        print("crawled")

    
    def create_new_json(self, target):
        with open('{}_data.json'.format(target),'w') as f:
            json.dump([{}],f,indent=4)
        
    def get_target_data(self,target,query):
        data = [{}]
        self.create_new_json(target)
        try:
            print("---reached --here")
            # 10.10.102.106

            socketIO = SocketIO('http://{0}'.format(settings.MC_IP), 8000, LoggingNamespace)
            # socketIO = SocketIO('http://192.168.18.183', 8000, LoggingNamespace)

            socketIO.on('connect', on_connect)
            id_u = uuid.uuid1()
            print(str(id_u))
            socketIO.emit('join',{'username':'','room':str(id_u)})
            if target == 'facebook':
                socketIO.on('{}_message'.format(target), facebook_message)
            if target == 'instagram':
                socketIO.on('{}_message'.format(target), instagram_message)
            if target == 'twitter':
                socketIO.on('{}_message'.format(target), twitter_message)
            if target == 'linkedin':
                socketIO.on('{}_message'.format(target), linkedin_message)
            if target == 'reddit':
                socketIO.on('{}_message'.format(target), reddit_message)
            if target == 'tiktok':
                socketIO.on('{}_message'.format(target), tiktok_message) 
            if target == 'tumblr':
                socketIO.on('{}_message'.format(target), tumblr_message) 
            if target == 'youtube':
                socketIO.on('{}_message'.format(target), youtube_message)
            if target == 'image_reverse_lookup':
                socketIO.on('{}_message'.format(target), image_reverse_lookup_message)

            if target == 'image_reverse_lookup':
                socketIO.emit('image_reverse_lookup', {'social_media':target,"query":query,'room':str(id_u)}, self.message1)
            else:
                socketIO.emit('message', {'social_media':target,"query":query,'room':str(id_u)}, self.message1)
            socketIO.wait_for_callbacks()
            with open('{}_data.json'.format(target)) as f:
                self.target_data = json.load(f)
        except:
            pass
      
    def start_targetidentify(self,target,query):
        # import threading
        # d = threading.Thread(target=self.get_target_data,args=(target,query))
        # d.start()
        # d.join()
        # self.create_new_json(target)
        data = self.get_target_data(target=target,query=query)
        return self.target_data