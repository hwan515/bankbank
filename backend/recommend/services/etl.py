import json
import ast

# 네 프로젝트 카테고리 코드가 이미 TRANS/SHOP/FOOD... 형태라
# 보통은 그대로 쓰면 됨. 혹시 한글이 들어오면 매핑으로 보정.
CATEGORY_MAP = {
    "교통": "TRANS",
    "카페": "COFFEE",
    "음식": "FOOD",
    "쇼핑": "SHOP",
    "편의점": "CONV",
    "통신": "PHONE",
    "문화": "CULTURE",
    "교육": "EDU",
    "의료": "MEDICAL",
    "뷰티": "BEAUTY",
    "생활": "LIFE",
    "주유": "OIL",
    "여행": "TRAVEL",
    "간편결제": "PAY",
    "공과금": "UTILITY",
    "해외": "OVERSEAS",
    "기타": "ETC",
}

KNOWN_CODES = set(CATEGORY_MAP.values())

def safe_json_loads(text: str):
    """
    structured_benefit가 TEXT로 저장되어 있으므로 안전하게 파싱.
    - 정상 JSON: json.loads
    - 혹시 파이썬 리터럴 형태면: ast.literal_eval 백업
    """
    if not text:
        return None
    try:
        return json.loads(text)
    except Exception:
        pass
    try:
        return ast.literal_eval(text)
    except Exception:
        return None

def normalize_category(raw):
    """
    raw가 이미 코드(TRANS/FOOD...)면 그대로,
    한글이면 CATEGORY_MAP으로 변환,
    그 외는 ETC로 처리
    """
    if not raw:
        return "ETC"
    raw = str(raw).strip()
    if raw in KNOWN_CODES:
        return raw
    return CATEGORY_MAP.get(raw, "ETC")

def _to_float(x):
    try:
        return float(x)
    except Exception:
        return None

def _to_int(x):
    try:
        # "10000" 같은 문자열도 처리
        return int(float(x))
    except Exception:
        return None

def normalize_one_benefit(b: dict):
    """
    원천 structured_benefit 항목 예시:
    {
        "category": "TRANS",
        "brand": "ALL",
        "type": "DISCOUNT",
        "value": 10,
        "unit": "PERCENT",
        "limit": 10000,
        "cond": 300000
    }

    반환 dict는 CardBenefitIndex 저장에 바로 쓸 수 있는 형태.
    """
    category = normalize_category(b.get("category"))
    brand = (b.get("brand") or "ALL")
    raw_type = (b.get("type") or "")
    unit = (b.get("unit") or "").upper()

    value = b.get("value")
    limit = b.get("limit")
    cond = b.get("cond")

    rate = None
    amount_won = None

    v = _to_float(value)
    if v is not None:
        if unit == "PERCENT":
            rate = v / 100.0
        elif unit in ("WON", "KRW"):
            amount_won = _to_int(v)

    limit_month_won = _to_int(limit)
    cond_min_spending = _to_int(cond)

    # 저장/디버깅용 텍스트
    title = f"{category} {raw_type}/{brand}"
    desc = f"value={value} unit={unit} limit={limit} cond={cond}"

    if rate is not None:
        benefit_type = "PERCENT"
    elif amount_won is not None:
        benefit_type = "WON"
    else:
        benefit_type = "UNKNOWN"

    return {
        "category": category,
        "brand": brand,
        "raw_type": raw_type,
        "benefit_type": benefit_type,
        "rate": rate,                         # 0.05 형태
        "amount_won": amount_won,             # 정액이면 값
        "limit_month_won": limit_month_won,   # 월 한도(원)
        "cond": cond_min_spending,            # 전월실적 조건(원)
        "title": title[:255],
        "desc": desc,
    }
