import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from BlogApp.api.serializers import PostSerializer


class BlogWSConsumer(AsyncWebsocketConsumer):
    channel_layer = get_channel_layer()

    async def connect(self):
        # Join the "blogs" group
        await self.channel_layer.group_add(
            "blogs",
            self.channel_name
        )
        print('Starting connection')
        await self.accept()

    async def disconnect(self, close_code):
        # Leave the "blogs" group
        await self.channel_layer.group_discard(
            "blogs",
            self.channel_name
        )
        print(f'Connection closed with code {close_code}')

    async def send_blog(self, event):
        # Send the blog to the WebSocket
        blog = event['blog']
        await self.send(text_data=json.dumps(blog))

    @staticmethod
    def send_new_blog(post):
        # Use the serializer to convert the Post object to a dictionary
        serialized_post = PostSerializer(post).data

        # Send the serialized post to the group
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            "blogs",
            {
                "type": "send_blog",
                "blog": serialized_post
            }
        )