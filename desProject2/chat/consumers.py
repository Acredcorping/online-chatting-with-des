import json
from chat.utils.msgEncryptAndDecrypt import msg_decrypt, msg_encrypt
from chat import models
from channels.generic.websocket import WebsocketConsumer
from channels.exceptions import StopConsumer

sockets = {}


class ChatConsumer(WebsocketConsumer):
    def websocket_connect(self, message):
        user_id = self.scope['url_route']['kwargs']['userid']
        obj_id = self.scope['url_route']['kwargs']['objid']
        sockets[f'{user_id}-{obj_id}'] = self
        self.accept()

    def websocket_receive(self, message):
        print(sockets)
        print(message)
        user_id = self.scope['url_route']['kwargs']['userid']
        obj_id = self.scope['url_route']['kwargs']['objid']
        key = models.SecretKey.objects.filter(user_id=user_id, obj_id=obj_id).first().key
        new_msg = models.Message.objects.create(sender_id=user_id, receiver_id=obj_id, content=msg_encrypt(message['text'], key))
        json_msg = json.dumps({
            'sender': new_msg.sender.username,
            'content': msg_decrypt(new_msg.content, key),
            'time': new_msg.create_time.strftime('%Y-%m-%dT%H:%M:%S')
        })
        self.send(json_msg)
        if f'{obj_id}-{user_id}' in sockets:
            sockets[f'{obj_id}-{user_id}'].send(json_msg)

    def websocket_disconnect(self, message):
        raise StopConsumer()
