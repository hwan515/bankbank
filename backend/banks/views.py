from django.shortcuts import render
import os
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny

KAKAO_DIRECTIONS_URL = "https://apis-navi.kakaomobility.com/v1/directions"
# Create your views here.


@api_view(["GET"])
@permission_classes([AllowAny])
def directions(request):
    """
    query:
      origin_lng, origin_lat
      dest_lng, dest_lat
    """
    origin_lng = request.GET.get("origin_lng")
    origin_lat = request.GET.get("origin_lat")
    dest_lng = request.GET.get("dest_lng")
    dest_lat = request.GET.get("dest_lat")
    
    if not all([origin_lng, origin_lat, dest_lng, dest_lat]):
        return JsonResponse({"detail": "missing params"}, status=400)

    rest_key = os.getenv("KAKAO_REST_API_KEY")
    if not rest_key:
        return JsonResponse({"detail": "KAKAO_REST_API_KEY not set"}, status=500)

    headers = {"Authorization": f"KakaoAK {rest_key}"}  # 공백 포함 중요 :contentReference[oaicite:1]{index=1}
    params = {
        "origin": f"{origin_lng},{origin_lat}",
        "destination": f"{dest_lng},{dest_lat}",
        # 필요하면 옵션 추가 (priority 등)
    }

    r = requests.get(KAKAO_DIRECTIONS_URL, headers=headers, params=params, timeout=10)
    if r.status_code != 200:
        return JsonResponse({"detail": "kakao directions error", "status": r.status_code, "body": r.text}, status=502)

    data = r.json()
   
    # ✅ 응답에서 polyline용 좌표 뽑기 (대표적으로 sections->roads->vertexes 형태를 많이 씀 :contentReference[oaicite:2]{index=2})
    path = []
    try:
        roads = data["routes"][0]["sections"][0]["roads"]
        for road in roads:
            v = road["vertexes"]  # [lng, lat, lng, lat, ...]
            for i in range(0, len(v), 2):
                path.append({"lng": v[i], "lat": v[i+1]})
    except Exception:
        return JsonResponse({"detail": "unexpected response shape", "raw": data}, status=502)

    return JsonResponse({"path": path})