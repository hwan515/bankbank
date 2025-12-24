import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "card_project.settings")

import django
django.setup()  # ✅ 이게 핵심 (settings/앱 로드)

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

from chats.middleware import TokenAuthMiddlewareStack
from chats.routing import websocket_urlpatterns

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": TokenAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
