from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from datetime import date, timedelta

from .services import load_price_chart_from_excel

def _resolve_range_to_dates(range_key: str | None):
    """range_key -> (start, end) 문자열("YYYY-MM-DD") 또는 (None, None)"""
    if not range_key:
        return (None, None)

    today = date.today()
    rk = range_key.lower()

    if rk == "7d":
        return ((today - timedelta(days=7)).isoformat(), today.isoformat())
    if rk == "1m":
        return ((today - timedelta(days=30)).isoformat(), today.isoformat())
    if rk == "3m":
        return ((today - timedelta(days=90)).isoformat(), today.isoformat())
    if rk == "6m":
        return ((today - timedelta(days=180)).isoformat(), today.isoformat())
    if rk == "1y":
        return ((today - timedelta(days=365)).isoformat(), today.isoformat())
    if rk == "ytd":
        return (date(today.year, 1, 1).isoformat(), today.isoformat())
    if rk == "max":
        return (None, None)

    return (None, None)

@api_view(["GET"])
def metal_chart(request):
    metal = request.GET.get("metal", "gold").lower()
    range_key = request.GET.get("range", "3m")  # 기본 3m
    rows = int(request.GET.get("rows", "60"))

    start = request.GET.get("start")
    end = request.GET.get("end")

    file_path = settings.METAL_PRICE_FILES.get(metal)
    if not file_path:
        return Response({"detail": "Invalid metal"}, status=400)

    series_name = "Gold" if metal == "gold" else "Silver"

    payload = load_price_chart_from_excel(
        file_path=str(file_path),
        series_name=series_name,
        range_key=range_key,   # ✅ 여기
        limit=rows,
        start=start if range_key == "custom" else None,
        end=end if range_key == "custom" else None,
    )
    return Response(payload)

