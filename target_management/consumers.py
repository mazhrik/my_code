from channels.generic.websocket import AsyncWebsocketConsumer, WebsocketConsumer
from asgiref.sync import async_to_sync
import json

# class MyConsumer(AsyncWebsocketConsumer):
#     groups = ["broadcast"]

#     async def connect(self):
#         # Called on connection.
#         # To accept the connection call:
#         await self.accept()
#         # Or accept the connection and specify a chosen subprotocol.
#         # A list of subprotocols specified by the connecting client
#         # will be available in self.scope['subprotocols']
#         await self.accept("subprotocol")
#         # To reject the connection, call:
#         await self.close()

#     async def receive(self, text_data=None, bytes_data=None):
#         # Called with either text_data or bytes_data for each frame
#         # You can call:
#         await self.send(text_data="Hello world!")
#         # Or, to send a binary frame:
#         await self.send(bytes_data="Hello world!")
#         # Want to force-close the connection? Call:
#         await self.close()
#         # Or add a custom WebSocket error code!
#         await self.close(code=4123)

#     async def disconnect(self, close_code):
#         # Called when the socket closes

class TestConsumer(WebsocketConsumer):
    # groups = ["broadcast"]
    #ws://

    def connect(self):
        # # Called on connection.
        # # To accept the connection call:
        # self.accept()
        # # Or accept the connection and specify a chosen subprotocol.
        # # A list of subprotocols specified by the connecting client
        # # will be available in self.scope['subprotocols']
        # self.accept("subprotocol")
        # # To reject the connection, call:
        # self.close()
        self.room_name = "test_consumer"
        self.room_group_name = "test_consumer_group"
        # async_to_sync( self.channel_layer.group_add)(
        #     self.room_name, self.room_group_name
        # )

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        self.send(text_data=json.dumps({"status":"connected"})) # this code is resposeable for sending data from backed to frentend

    def receive(self,text_data):


        """when ever you want to receive data form frentend you will be using this code."""
        text_data_json = json.loads(text_data)
        message = text_data_json['message']

        self.send(text_data=json.dumps({
            'message': message+" yes backend recive the data now im  'server'"
        }))

        
        

    def disconnect(self  ):
        self.send(text_data=json.dumps({
            'message': "you are disconnected"
        }))
    # def receive(self, text_data=None, bytes_data=None):
    #     # Called with either text_data or bytes_data for each frame
    #     # You can call:
    #     self.send(text_data="Hello world!")
    #     # Or, to send a binary frame:
    #     self.send(bytes_data="Hello world!")
    #     # Want to force-close the connection? Call:
    #     self.close()
    #     # Or add a custom WebSocket error code!
    #     self.close(code=4123)

    # def disconnect(self, close_code):
    #     # Called when the socket closes
    #     pass

    def send_notification(self, event ):
        print("yes its working bitch")
        print(event)

        self.send(text_data=json.dumps({"status":"yes its connected"}))
        print("yoooo yeeaaaaah")


class ChatConsumer(WebsocketConsumer):


    def connect(self):
        self.room_name = 'room'
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, close_code):
        # leave group room
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )
        self.send(text_data=json.dumps({
            'message': "you are disconnected"
        }))

    def receive(self, text_data):
        data = json.loads(text_data)
        self.commands[data['command']](self, data)