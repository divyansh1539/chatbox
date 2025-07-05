from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import async_to_sync
import json

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        # Get the actual room name from URL
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = "global_broadcast_group"  # Common broadcast group

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        self.accept()

    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        username = data.get('username')
        room = self.room_name  # get current room name

        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'room': room
            }
        )

    def chat_message(self, event):
        message = event['message']
        username = event['username']
        room = event['room']

        self.send(text_data=json.dumps({
            'message': f"[{room}] {username}: {message}"
        }))
