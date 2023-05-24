from django.urls import re_path

from chat import consumers

websocket_urlpatterns = [
    re_path(r'chat/(?P<userid>\w+)&(?P<objid>\w+)/$', consumers.ChatConsumer.as_asgi()),
]
