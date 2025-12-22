import requests
import pandas as pd

GOLD_URL = "https://apis.data.go.kr/1160100/service/GetGeneralProductInfoService/getGoldPriceInfo"

def load_gold_price_chart(service_key: str, num_of_rows: int = 60, page_no: int = 1):
    params = {
        "serviceKey": service_key,
        "resultType": "json",
        "numOfRows": num_of_rows,
        "pageNo": page_no,
    }

    res = requests.get(GOLD_URL, params=params, timeout=10)
    res.raise_for_status()

    data = res.json()
    items = data["response"]["body"]["items"]["item"]

    df = pd.DataFrame(items)
    if df.empty:
        return {"labels": [], "series": []}

    # 정리
    df["itmsNm"] = df["itmsNm"].str.replace(r"\s+", " ", regex=True).str.strip()
    df["basDt"] = pd.to_datetime(df["basDt"], format="%Y%m%d")
    df["clpr"] = pd.to_numeric(df["clpr"], errors="coerce")

    df = df.dropna(subset=["basDt", "clpr"]).sort_values(["itmsNm", "basDt"])

    # labels (전체 날짜 축)
    labels = sorted(df["basDt"].dt.strftime("%Y-%m-%d").unique().tolist())

    # 상품별 series 만들기 (Chart.js friendly)
    series = []
    for name, g in df.groupby("itmsNm"):
        m = {d: v for d, v in zip(g["basDt"].dt.strftime("%Y-%m-%d"), g["clpr"])}
        series.append({
            "name": name,
            "data": [m.get(d, None) for d in labels],  # 날짜 없는 날은 null
        })

    return {"labels": labels, "series": series}
