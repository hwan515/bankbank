from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
import requests
# Create your views here.

# 유튜브에서 데이터를 가져옵니다. 
@api_view(['GET'])
def load(request):
    url = "https://www.googleapis.com/youtube/v3/search"
    param = {
        "key":settings.YOUTUBE_API_KEY,
        "part": "snippet",
        "q": "주식",
        "type": "video",
        "maxResults": 10,
    }
    res = requests.get(url=url, params=param)

    return Response(res.json())


# 유튜브에서 데이터를 가져옵니다. 
@api_view(['GET'])
def search(request):
    q = request.GET.get('q', '')
    print(q)
    url = "https://www.googleapis.com/youtube/v3/search"
    param = {
        "key":settings.YOUTUBE_API_KEY,
        "part": "snippet",
        "q": q,
        "type": "video",
        "maxResults": 10,
    }
    res = requests.get(url=url, params=param)

    if res.status_code != 200:
        return Response({"error": res.text}, status=res.status_code)
    return Response(res.json())