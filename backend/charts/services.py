import pandas as pd
from datetime import timedelta, date

def _range_to_start_end(range_key: str, anchor: date):
    rk = (range_key or "").lower()
    if rk == "7d":
        return anchor - timedelta(days=7), anchor
    if rk == "1m":
        return anchor - timedelta(days=30), anchor
    if rk == "3m":
        return anchor - timedelta(days=90), anchor
    if rk == "6m":
        return anchor - timedelta(days=180), anchor
    if rk == "1y":
        return anchor - timedelta(days=365), anchor
    if rk == "ytd":
        return date(anchor.year, 1, 1), anchor
    if rk == "max":
        return None, None
    return None, None

def load_price_chart_from_excel(
    file_path: str,
    series_name: str,
    range_key: str | None = None,   # ✅ 추가
    limit: int | None = None,
    start: str | None = None,
    end: str | None = None,
):
    df = pd.read_excel(file_path)

    if df.empty or "Date" not in df.columns or "Close/Last" not in df.columns:
        return {"labels": [], "series": []}

    df = df[["Date", "Close/Last"]].copy()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df["Close/Last"] = (
        df["Close/Last"].astype(str).str.replace(",", "", regex=False).str.strip()
    )
    df["Close/Last"] = pd.to_numeric(df["Close/Last"], errors="coerce")

    df = df.dropna(subset=["Date", "Close/Last"]).sort_values("Date")

    if df.empty:
        return {"labels": [], "series": []}

    # ✅ 기준 날짜를 "데이터 최신 날짜"로 잡음
    anchor = df["Date"].max().date()

    # ✅ range_key가 있고 custom이 아니면 range로 start/end 생성
    if range_key and range_key.lower() not in ("custom",):
        s, e = _range_to_start_end(range_key, anchor)
        if s:
            df = df[df["Date"] >= pd.Timestamp(s)]
        if e:
            df = df[df["Date"] <= pd.Timestamp(e)]

    # ✅ custom start/end 처리
    if start:
        s = pd.to_datetime(start, errors="coerce")
        if pd.notna(s):
            df = df[df["Date"] >= s]
    if end:
        e = pd.to_datetime(end, errors="coerce")
        if pd.notna(e):
            df = df[df["Date"] <= e]

    # ✅ 아무 필터도 없을 때만 limit
    if (not range_key or range_key.lower() == "max") and (not start and not end) and limit:
        df = df.tail(limit)

    labels = df["Date"].dt.strftime("%Y-%m-%d").tolist()
    data = df["Close/Last"].tolist()

    return {"labels": labels, "series": [{"name": series_name, "data": data}]}
