from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import GmsChatbotService


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def chatbot(request):
    message = (request.data.get("message") or "").strip()
    if not message:
        return Response(
            {"detail": "message is required."},
            status=status.HTTP_400_BAD_REQUEST,
        )

    service = GmsChatbotService()
    payload = service.handle_message(request.user, message)
    return Response(payload, status=status.HTTP_200_OK)
