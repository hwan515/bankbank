from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from .services import load_gold_price_chart

@api_view(["GET"])
def gold_chart(request):
    payload = load_gold_price_chart(service_key=settings.DATA_GO_KR_KEY, num_of_rows=60, page_no=1)
    return Response(payload)