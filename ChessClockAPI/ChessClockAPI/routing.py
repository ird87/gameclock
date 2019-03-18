from django.urls import path

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, ChannelNameRouter,  URLRouter
from chess_clock.consumers import Consumer


application = ProtocolTypeRouter({
    # (http->django views is added by default)
    "websocket": AuthMiddlewareStack(
        URLRouter([
            path('user/<full_url>', Consumer, name="websocket_connect"),
            # path('<short_url>', Consumer, name="websocket_connect"),
        ])
    ),
})




# channel_routing = {
#     'websocket.connect': 'chess_clock.consumers.websocket_connect',
#     'websocket.receive': 'chess_clock.consumers.websocket_message',
#     'websocket.disconnect': 'chess_clock.consumers.websocket_disconnect',
#     'send_pause': 'chess_clock.consumers .set_pause'
# }




