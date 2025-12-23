import os
import re
import json
import time
import random
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI

# ======================
# 0) Config
# ======================
load_dotenv()

GMS_API_KEY = os.getenv("GMS_KEY")
DB_NAME = os.getenv("DB_NAME", "card_gorilla_master.db")
MODEL = os.getenv("GMS_MODEL", "gpt-4o-mini")
TOP_N = int(os.getenv("TOP_N", "10"))

MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "8000"))
MAX_RETRIES = 3
SLEEP_BETWEEN_CALLS = 0.4
BATCH_COMMIT = 10
TEMPERATURE = 0.0

ALLOWED_CATEGORY = {
    "교통", "통신", "쇼핑", "카페", "음식", "주유",
    "공과금", "구독", "간편결제", "문화", "여행", "의료", "교육", "기타"
}

# ======================
# 1) Structured Outputs (v2)
# ======================
BENEFIT_RULES_V2_RESPONSE_FORMAT = {
    "type": "json_schema",
    "json_schema": {
        "name": "benefit_rules_v2",
        "strict": True,
        "schema": {
            "type": "object",
            "additionalProperties": False,
            "required": ["version", "items"],
            "properties": {
                "version": {"type": "integer", "enum": [2]},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "additionalProperties": False,
                        "required": [
                            "category", "brand",
                            "benefit_type",
                            "scope",
                            "calc_method",
                            "value", "value_unit", "per_won",
                            "min_total_spend_won",
                            "weekend_only", "weekday_only",
                            "min_tx_won", "max_tx_won",
                            "per_tx_cap", "per_tx_cap_unit",
                            "max_uses_per_month",
                            "monthly_cap", "monthly_cap_unit",
                            "cap_is_shared", "cap_group"
                        ],
                        "properties": {
                            "category": {"type": "string", "enum": list(ALLOWED_CATEGORY)},
                            "brand": {"type": "string"},

                            "benefit_type": {"type": "string", "enum": ["할인", "적립"]},
                            "scope": {"type": "string", "enum": ["CATEGORY", "TOTAL"]},

                            "calc_method": {"type": "string", "enum": ["PERCENT", "FIXED", "PER_WON", "PER_LITER"]},

                            "value": {"type": "number", "minimum": 0},
                            "value_unit": {"type": "string", "enum": ["퍼센트", "원", "마일", "점"]},

                            # PER_WON: N원당 X마일/점일 때 N
                            # 그 외는 0
                            "per_won": {"type": "integer", "minimum": 0},

                            # 전월실적 조건(텍스트에 없으면 0)
                            "min_total_spend_won": {"type": "integer", "minimum": 0, "multipleOf": 10000},

                            "weekend_only": {"type": "boolean"},
                            "weekday_only": {"type": "boolean"},

                            # 건당 최소/최대 적용 금액(텍스트에 없으면 0)
                            "min_tx_won": {"type": "integer", "minimum": 0},
                            "max_tx_won": {"type": "integer", "minimum": 0},

                            # 건당 혜택 상한(예: 건당 할인한도 2,200원)
                            "per_tx_cap": {"type": "number", "minimum": 0},
                            "per_tx_cap_unit": {"type": "string", "enum": ["원", "점", "마일", "없음"]},

                            # 월 제공 횟수(없으면 0 = 무제한으로 간주)
                            "max_uses_per_month": {"type": "integer", "minimum": 0},

                            # 월 한도(없으면 0)
                            "monthly_cap": {"type": "number", "minimum": 0},
                            "monthly_cap_unit": {"type": "string", "enum": ["원", "점", "마일", "없음"]},

                            # 통합 한도 처리
                            "cap_is_shared": {"type": "boolean"},
                            "cap_group": {"type": "string"}
                        }
                    }
                }
            }
        }
    }
}

SYSTEM_PROMPT_V2 = """
당신은 신용카드 혜택 텍스트를 '계산기용 룰(v2)'로 정형화하는 분석가입니다.
반드시 response_format의 JSON Schema에 정확히 맞는 JSON만 출력하세요.

[추측 금지]
- 입력 텍스트에 없는 숫자는 절대 만들지 마세요.
- 전월실적 조건(min_total_spend_won)이 텍스트에 없으면 0.
- 월 한도(monthly_cap)이 텍스트에 없으면 0.
- 횟수(max_uses_per_month)가 텍스트에 없으면 0(=무제한).
- 주말/주중 여부를 텍스트에서 명확히 알 수 없으면 weekend_only=false, weekday_only=false.
- 통합한도(공통/통합/공통사항/통합 월 1만원 등)가 명시되면 cap_is_shared=true, cap_group은 같은 문자열로 통일.
  예: "통합할인한도" 같은 표현이 있으면 cap_group="INTEGRATED_1".

[필드 매핑]
- category: 교통/통신/쇼핑/카페/음식/주유/공과금/구독/간편결제/문화/여행/의료/교육/기타 중 하나
- brand: "커피전문점", "스타벅스", "CGV", "모든가맹점" 등 텍스트에서 읽힌 대상
- benefit_type: 할인/적립

- scope:
  - "모든 가맹점", "국내 가맹점" 등 총지출 기준이면 "TOTAL"
  - 그 외는 "CATEGORY"

- calc_method:
  - "10% 할인/적립" -> PERCENT
  - "5,000원 할인" -> FIXED
  - "1,000원당 1마일(점)" -> PER_WON (per_won=1000, value=1, value_unit=마일/점)
  - "리터당 60원" / "원/L" -> PER_LITER (value=60, value_unit=원)

- min_tx_won:
  - "1회 이용금액 1만원 이상" -> 10000
- max_tx_won:
  - "1회 5만원까지" -> 50000
- per_tx_cap:
  - "건당 할인한도 2,200원" -> per_tx_cap=2200, per_tx_cap_unit="원"
- max_uses_per_month:
  - "월 3회" -> 3
- monthly_cap:
  - "통합 월 10,000원" -> monthly_cap=10000, monthly_cap_unit="원"
  - 없으면 0, "없음"

[출력 예]
{"version":2,"items":[ ... ]}
""".strip()

# ======================
# 2) OpenAI Client
# ======================
def get_client() -> OpenAI:
    if not GMS_API_KEY:
        raise RuntimeError("환경변수 GMS_KEY가 없습니다.")
    return OpenAI(api_key=GMS_API_KEY, base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1")

# ======================
# 3) DB Helpers
# ======================
def has_column(conn: sqlite3.Connection, table: str, col: str) -> bool:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in cur.fetchall())

def ensure_columns(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='cards'")
    if cur.fetchone()[0] == 0:
        raise RuntimeError("'cards' 테이블이 없습니다.")

    columns_to_add = {
        "structured_benefit_raw": "TEXT",
        "structured_benefit_error": "TEXT",
    }
    for col, col_type in columns_to_add.items():
        if not has_column(conn, "cards", col):
            cur.execute(f"ALTER TABLE cards ADD COLUMN {col} {col_type}")
            conn.commit()

# ======================
# 4) Parsing Utils
# ======================
def strip_code_fence(s: str) -> str:
    s = s.strip()
    if s.startswith("```"):
        lines = s.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        s = "\n".join(lines)
    return s.strip()

def to_scalar(v: Any) -> float:
    if v is None:
        return 0.0
    if isinstance(v, (int, float)):
        return float(v)
    s = str(v).replace(",", "").strip()
    m = re.search(r"[-+]?\d+(?:\.\d+)?", s)
    return float(m.group(0)) if m else 0.0

def to_won(v: Any) -> int:
    if v is None:
        return 0
    if isinstance(v, (int, float)):
        return int(round(v))
    s = str(v).replace(",", "").strip()
    m = re.search(r"([-+]?\d+(?:\.\d+)?)\s*(만|천|백)?\s*원?", s)
    if m:
        num = float(m.group(1))
        unit = m.group(2)
        factor = {"만": 10000, "천": 1000, "백": 100}.get(unit, 1)
        return int(round(num * factor))
    return int(round(to_scalar(s)))

# ======================
# 5) Build LLM Input (benefits_json -> text)
# ======================
def _pick_useful_lines(detail: str) -> List[str]:
    if not detail:
        return []
    out = []
    for line in detail.splitlines():
        line = line.strip()
        if not line:
            continue
        if re.search(r"\d", line) or any(k in line for k in ["월", "일", "회", "이상", "까지", "통합", "주말", "주중", "한도", "건당", "리터"]):
            out.append(line)
    return out[:12]

def build_input_text(benefits_json_str: str, max_chars: int) -> Optional[str]:
    try:
        raw_list = json.loads(benefits_json_str)
        if not isinstance(raw_list, list):
            return None
    except Exception:
        return None

    lines: List[str] = []
    for item in raw_list:
        if not isinstance(item, dict):
            continue

        title = str(item.get("title", "")).strip()
        if "유의사항" in title:
            continue

        summary = str(item.get("summary", "")).strip()
        detail = str(item.get("detail", "")).strip()

        useful = _pick_useful_lines(detail)
        merged = summary
        if useful:
            merged = (summary + "\n" + "\n".join(useful)).strip()

        if not title and not merged:
            continue

        lines.append(f"- {title}: {merged}")

    if not lines:
        return None

    text = "\n".join(lines)
    return text[:max_chars]

# ======================
# 6) LLM Call (Structured Outputs)
# ======================
def call_llm_with_retry(client: OpenAI, text: str) -> str:
    last_err: Optional[Exception] = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT_V2},
                    {"role": "user", "content": text},
                ],
                temperature=TEMPERATURE,
                response_format=BENEFIT_RULES_V2_RESPONSE_FORMAT,
            )
            return (resp.choices[0].message.content or "").strip()
        except Exception as e:
            last_err = e
            time.sleep((1 * attempt) + random.uniform(0, 1))
    raise RuntimeError(f"LLM 호출 실패: {last_err}")

# ======================
# 7) Normalize & Store
# ======================
def normalize_rule_v2(x: Dict[str, Any]) -> Dict[str, Any]:
    # strict schema로 받는다고 가정하지만, DB 안정성을 위해 최소한 정리
    cat = str(x.get("category", "기타")).strip()
    if cat not in ALLOWED_CATEGORY:
        cat = "기타"
    brand = str(x.get("brand", "ALL")).strip()

    benefit_type = x.get("benefit_type", "할인")
    if benefit_type not in ("할인", "적립"):
        benefit_type = "할인"

    scope = x.get("scope", "CATEGORY")
    if scope not in ("CATEGORY", "TOTAL"):
        scope = "CATEGORY"

    calc_method = x.get("calc_method", "PERCENT")
    if calc_method not in ("PERCENT", "FIXED", "PER_WON", "PER_LITER"):
        calc_method = "PERCENT"

    value = float(to_scalar(x.get("value", 0)))
    value_unit = x.get("value_unit", "원")
    if value_unit not in ("퍼센트", "원", "마일", "점"):
        value_unit = "원"

    per_won = max(0, to_won(x.get("per_won", 0)))
    min_total_spend_won = max(0, (to_won(x.get("min_total_spend_won", 0)) // 10000) * 10000)

    weekend_only = bool(x.get("weekend_only", False))
    weekday_only = bool(x.get("weekday_only", False))

    min_tx_won = max(0, to_won(x.get("min_tx_won", 0)))
    max_tx_won = max(0, to_won(x.get("max_tx_won", 0)))

    per_tx_cap = float(to_scalar(x.get("per_tx_cap", 0)))
    per_tx_cap_unit = x.get("per_tx_cap_unit", "없음")
    if per_tx_cap_unit not in ("원", "점", "마일", "없음"):
        per_tx_cap_unit = "없음"

    max_uses_per_month = max(0, to_won(x.get("max_uses_per_month", 0)))

    monthly_cap = float(to_scalar(x.get("monthly_cap", 0)))
    monthly_cap_unit = x.get("monthly_cap_unit", "없음")
    if monthly_cap_unit not in ("원", "점", "마일", "없음"):
        monthly_cap_unit = "없음"

    cap_is_shared = bool(x.get("cap_is_shared", False))
    cap_group = str(x.get("cap_group", "")).strip()

    return {
        "category": cat,
        "brand": brand,
        "benefit_type": benefit_type,
        "scope": scope,
        "calc_method": calc_method,
        "value": value,
        "value_unit": value_unit,
        "per_won": per_won,
        "min_total_spend_won": min_total_spend_won,
        "weekend_only": weekend_only,
        "weekday_only": weekday_only,
        "min_tx_won": min_tx_won,
        "max_tx_won": max_tx_won,
        "per_tx_cap": per_tx_cap,
        "per_tx_cap_unit": per_tx_cap_unit,
        "max_uses_per_month": max_uses_per_month,
        "monthly_cap": monthly_cap,
        "monthly_cap_unit": monthly_cap_unit,
        "cap_is_shared": cap_is_shared,
        "cap_group": cap_group,
    }

def parse_llm_output_v2(raw: str) -> Dict[str, Any]:
    raw = strip_code_fence(raw)
    try:
        data = json.loads(raw)
    except Exception as e:
        raise RuntimeError(f"JSON parse 실패: {e}")

    if not isinstance(data, dict) or data.get("version") != 2 or not isinstance(data.get("items"), list):
        raise RuntimeError("스키마 불일치")

    items = []
    for x in data["items"][:60]:
        if isinstance(x, dict):
            items.append(normalize_rule_v2(x))
    return {"version": 2, "items": items}

# ======================
# 8) Refine Top Cards (DB update)
# ======================
def refine_top_cards_v2() -> None:
    client = get_client()
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        ensure_columns(conn)
        ranking_exists = has_column(conn, "cards", "ranking")

        query = """
            SELECT gorilla_id, name, benefits_json, min_spending, structured_benefit
            FROM cards
            WHERE (structured_benefit IS NULL OR structured_benefit = '')
        """
        if ranking_exists:
            query += f" AND ranking IS NOT NULL AND ranking <= {TOP_N} ORDER BY ranking ASC"
        else:
            query += f" LIMIT {TOP_N}"

        cur.execute(query)
        cards = cur.fetchall()
        print(f"v2 정형화 대상: {len(cards)}개")

        ok = 0
        fail = 0
        pending = 0

        for idx, row in enumerate(cards, start=1):
            g_id = row["gorilla_id"]
            name = row["name"]
            benefits_json_str = row["benefits_json"]

            text = build_input_text(benefits_json_str, MAX_INPUT_CHARS)
            if not text:
                print(f"[{idx}] {name}: 혜택 데이터 없음 (Skip)")
                fail += 1
                continue

            print(f"[{idx}] {name} 분석 중...", end=" ", flush=True)

            try:
                raw = call_llm_with_retry(client, text)
                parsed_obj = parse_llm_output_v2(raw)

                json_str_db = json.dumps(parsed_obj, ensure_ascii=False, separators=(",", ":"))

                ucur = conn.cursor()
                ucur.execute(
                    """UPDATE cards SET
                        structured_benefit = ?,
                        structured_benefit_raw = ?,
                        structured_benefit_error = NULL
                       WHERE gorilla_id = ?""",
                    (json_str_db, raw, g_id),
                )

                ok += 1
                pending += 1
                print(f"성공 (items={len(parsed_obj['items'])}) ✅")

                if pending >= BATCH_COMMIT:
                    conn.commit()
                    pending = 0

            except Exception as e:
                fail += 1
                print(f"실패 ❌: {e}")
                ucur = conn.cursor()
                ucur.execute(
                    "UPDATE cards SET structured_benefit_error = ?, structured_benefit_raw = ? WHERE gorilla_id = ?",
                    (str(e), None, g_id),
                )

            time.sleep(SLEEP_BETWEEN_CALLS + random.uniform(0, 0.3))

        if pending > 0:
            conn.commit()

        print(f"\n완료: 성공={ok}, 실패={fail}, 총={len(cards)}")

    finally:
        conn.close()

# ======================
# 9) Calculator v2
# ======================
SpendProfile = Dict[str, Dict[str, Any]]

def _sum_total_spend(profile: SpendProfile) -> int:
    total = 0
    for cat, obj in profile.items():
        if not isinstance(obj, dict):
            continue
        total += to_won(obj.get("amount", 0))
    return total

def _get_cat_amount(profile: SpendProfile, category: str) -> int:
    obj = profile.get(category, {})
    return to_won(obj.get("amount", 0)) if isinstance(obj, dict) else 0

def _get_tx_count(profile: SpendProfile, category: str, amount: int) -> int:
    obj = profile.get(category, {})
    if not isinstance(obj, dict):
        return 1
    tx = obj.get("tx_count")
    if tx is None:
        return 1
    try:
        txi = int(tx)
        return max(1, txi)
    except Exception:
        return 1

def _get_weekend_ratio(profile: SpendProfile, category: str) -> Optional[float]:
    obj = profile.get(category, {})
    if not isinstance(obj, dict):
        return None
    r = obj.get("weekend_ratio")
    if r is None:
        return None
    try:
        rf = float(r)
        if 0.0 <= rf <= 1.0:
            return rf
        return None
    except Exception:
        return None

def _cap(value: float, cap_value: float) -> float:
    if cap_value <= 0:
        return value
    return min(value, cap_value)

def estimate_card_value_v2(
    rules_obj: Dict[str, Any],
    spend_profile: SpendProfile,
    card_min_spending_won: int,
    *,
    fuel_price_won_per_liter: Optional[int] = None,   # 주유 PER_LITER 계산 시 필요
    mile_to_won: float = 0.0,                         # 마일을 원으로 환산(모르면 0)
    point_to_won: float = 1.0                         # 점수 환산(대부분 1점=1원이라 기본 1)
) -> Dict[str, Any]:
    total_spend = _sum_total_spend(spend_profile)
    card_min_spending_won = to_won(card_min_spending_won)

    # 전월실적을 "이번 달 지출"로 대체하는 계산이므로 현실과 다를 수 있음(추정)
    card_eligible = (card_min_spending_won == 0) or (total_spend >= card_min_spending_won)

    items = rules_obj.get("items", [])
    if not isinstance(items, list):
        items = []

    # shared cap 그룹 누적
    shared_group_sum: Dict[str, Dict[str, float]] = {}  # group -> {"원":x,"점":y,"마일":z,"cap":c,"cap_unit":u}

    lines = []
    total_discount_won = 0.0
    total_points = 0.0
    total_miles = 0.0

    for r in items:
        if not isinstance(r, dict):
            continue

        category = r["category"]
        scope = r["scope"]

        base_amount = total_spend if scope == "TOTAL" else _get_cat_amount(spend_profile, category)

        if base_amount <= 0:
            continue

        # 주말/주중 조건 처리 (ratio 없으면 0으로 계산)
        if r["weekend_only"]:
            ratio = _get_weekend_ratio(spend_profile, category)
            base_amount = int(round(base_amount * (ratio if ratio is not None else 0.0)))
        elif r["weekday_only"]:
            ratio = _get_weekend_ratio(spend_profile, category)
            # weekday = 1 - weekend
            base_amount = int(round(base_amount * (1.0 - ratio))) if ratio is not None else 0

        if base_amount <= 0:
            continue

        rule_min = to_won(r.get("min_total_spend_won", 0))
        rule_eligible = (rule_min == 0) or (total_spend >= rule_min)

        applied = bool(card_eligible and rule_eligible)

        tx_count = _get_tx_count(spend_profile, category, base_amount)
        uses = tx_count
        max_uses = int(r.get("max_uses_per_month", 0) or 0)
        if max_uses > 0:
            uses = min(uses, max_uses)

        avg_tx = base_amount / max(1, tx_count)

        min_tx = to_won(r.get("min_tx_won", 0))
        max_tx = to_won(r.get("max_tx_won", 0))

        # 분포를 모르므로 평균 기반으로만 근사(정확하지 않을 수 있음)
        tx_base = avg_tx
        if max_tx > 0:
            tx_base = min(tx_base, float(max_tx))

        # 최소 이용금액 조건(평균이 미달이면 전체 미적용으로 보수 계산)
        if min_tx > 0 and tx_base < min_tx:
            applied = False

        discount_won = 0.0
        points = 0.0
        miles = 0.0

        if applied and uses > 0:
            calc_method = r["calc_method"]
            value = float(r["value"])
            value_unit = r["value_unit"]
            per_won = to_won(r.get("per_won", 0))

            per_tx_cap = float(r.get("per_tx_cap", 0.0))
            per_tx_cap_unit = r.get("per_tx_cap_unit", "없음")

            # 월 한도(단독 캡일 수도, 통합 캡일 수도)
            monthly_cap = float(r.get("monthly_cap", 0.0))
            monthly_cap_unit = r.get("monthly_cap_unit", "없음")

            cap_is_shared = bool(r.get("cap_is_shared", False))
            cap_group = str(r.get("cap_group", "")).strip()

            for _ in range(uses):
                if calc_method == "PERCENT":
                    if value_unit != "퍼센트":
                        continue
                    d = tx_base * (value / 100.0)
                    if per_tx_cap_unit == "원" and per_tx_cap > 0:
                        d = _cap(d, per_tx_cap)
                    discount_won += d

                elif calc_method == "FIXED":
                    if value_unit != "원":
                        continue
                    d = min(float(value), float(tx_base))
                    if per_tx_cap_unit == "원" and per_tx_cap > 0:
                        d = _cap(d, per_tx_cap)
                    discount_won += d

                elif calc_method == "PER_WON":
                    if per_won <= 0:
                        continue
                    mult = tx_base / float(per_won)
                    if value_unit == "점":
                        p = mult * value
                        if per_tx_cap_unit == "점" and per_tx_cap > 0:
                            p = _cap(p, per_tx_cap)
                        points += p
                    elif value_unit == "마일":
                        m = mult * value
                        if per_tx_cap_unit == "마일" and per_tx_cap > 0:
                            m = _cap(m, per_tx_cap)
                        miles += m

                elif calc_method == "PER_LITER":
                    # liters = amount / fuel_price
                    if fuel_price_won_per_liter is None or fuel_price_won_per_liter <= 0:
                        # 계산 불가 -> 0
                        continue
                    liters = tx_base / float(fuel_price_won_per_liter)
                    d = liters * value  # value is won per liter
                    if per_tx_cap_unit == "원" and per_tx_cap > 0:
                        d = _cap(d, per_tx_cap)
                    discount_won += d

            # 단독 월 한도 캡
            if not cap_is_shared:
                if monthly_cap_unit == "원" and monthly_cap > 0:
                    discount_won = _cap(discount_won, monthly_cap)
                elif monthly_cap_unit == "점" and monthly_cap > 0:
                    points = _cap(points, monthly_cap)
                elif monthly_cap_unit == "마일" and monthly_cap > 0:
                    miles = _cap(miles, monthly_cap)

            # 통합 월 한도 그룹 누적(그룹에서 캡)
            if cap_is_shared and cap_group:
                g = shared_group_sum.setdefault(cap_group, {"원": 0.0, "점": 0.0, "마일": 0.0, "cap": 0.0, "cap_unit": "없음"})
                g["원"] += discount_won
                g["점"] += points
                g["마일"] += miles

                # 그룹 캡은 룰들 중 "가장 작은 cap"을 적용(보수적)
                if monthly_cap > 0 and monthly_cap_unit != "없음":
                    if g["cap"] == 0:
                        g["cap"] = monthly_cap
                        g["cap_unit"] = monthly_cap_unit
                    else:
                        if monthly_cap_unit == g["cap_unit"]:
                            g["cap"] = min(g["cap"], monthly_cap)

                # 그룹이면 개별 합계에 지금 더하지 않고, 마지막에 그룹 캡 적용 후 반영
                discount_won = 0.0
                points = 0.0
                miles = 0.0

        # 개별(비그룹) 합산
        total_discount_won += discount_won
        total_points += points
        total_miles += miles

        lines.append({
            "category": category,
            "brand": r.get("brand", "ALL"),
            "benefit_type": r.get("benefit_type"),
            "scope": r.get("scope"),
            "calc_method": r.get("calc_method"),
            "applied": applied,
            "base_amount": base_amount,
            "tx_count_used": uses,
            "estimated_discount_won": int(round(discount_won)),
            "estimated_points": points,
            "estimated_miles": miles,
            "cap_is_shared": bool(r.get("cap_is_shared", False)),
            "cap_group": r.get("cap_group", ""),
        })

    # 통합 한도 그룹 처리 후 합산
    for group, g in shared_group_sum.items():
        cap = float(g.get("cap", 0.0))
        cap_unit = g.get("cap_unit", "없음")

        if cap_unit == "원" and cap > 0:
            total_discount_won += _cap(g["원"], cap)
        else:
            total_discount_won += g["원"]

        if cap_unit == "점" and cap > 0:
            total_points += _cap(g["점"], cap)
        else:
            total_points += g["점"]

        if cap_unit == "마일" and cap > 0:
            total_miles += _cap(g["마일"], cap)
        else:
            total_miles += g["마일"]

    # 환산(선택)
    total_value_won = float(total_discount_won) + (total_points * point_to_won) + (total_miles * mile_to_won)

    return {
        "eligible": card_eligible,
        "total_spend_input_won": total_spend,
        "card_min_spending_won": card_min_spending_won,
        "total_discount_won": int(round(total_discount_won)),
        "total_points": total_points,
        "total_miles": total_miles,
        "total_value_won_with_conversion": int(round(total_value_won)),
        "lines": lines,
    }

def recommend_cards_v2(
    spend_profile: SpendProfile,
    top_n: int = 10,
    *,
    fuel_price_won_per_liter: Optional[int] = None,
    mile_to_won: float = 0.0,
    point_to_won: float = 1.0
) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        SELECT gorilla_id, name, company, min_spending, structured_benefit
        FROM cards
        WHERE structured_benefit IS NOT NULL AND structured_benefit != ''
    """)
    rows = cur.fetchall()
    conn.close()

    results = []
    for row in rows:
        sb = row["structured_benefit"]
        try:
            rules_obj = json.loads(sb)
        except Exception:
            continue

        # v2 저장 형식: {"version":2,"items":[...]}
        if not (isinstance(rules_obj, dict) and rules_obj.get("version") == 2):
            continue

        est = estimate_card_value_v2(
            rules_obj,
            spend_profile,
            card_min_spending_won=(row["min_spending"] or 0),
            fuel_price_won_per_liter=fuel_price_won_per_liter,
            mile_to_won=mile_to_won,
            point_to_won=point_to_won,
        )

        results.append({
            "gorilla_id": row["gorilla_id"],
            "name": row["name"],
            "company": row["company"],
            "eligible": est["eligible"],
            "total_discount_won": est["total_discount_won"],
            "total_points": est["total_points"],
            "total_miles": est["total_miles"],
            "total_value_won_with_conversion": est["total_value_won_with_conversion"],
        })

    # 정렬: (1) eligible 우선 (2) 환산 합계(원) (3) 할인(원)
    results.sort(key=lambda x: (
        0 if x["eligible"] else 1,
        -x["total_value_won_with_conversion"],
        -x["total_discount_won"],
    ))
    return results[:top_n]

# ======================
# 10) Example Run
# ======================
if __name__ == "__main__":
    # 1) 먼저 v2 정형화 실행(필요한 경우)
    refine_top_cards_v2()

    # 2) 월 지출 입력 (최소 입력: amount만)
    spend_profile: SpendProfile = {
        "카페": {"amount": 120000, "tx_count": 12, "weekend_ratio": 0.3},
        "쇼핑": {"amount": 400000, "tx_count": 8},
        "교통": {"amount": 80000, "tx_count": 40},
        "통신": {"amount": 60000, "tx_count": 1},
        "음식": {"amount": 250000, "tx_count": 15, "weekend_ratio": 0.5},
        "주유": {"amount": 200000, "tx_count": 3},
    }

    recs = recommend_cards_v2(
        spend_profile,
        top_n=10,
        fuel_price_won_per_liter=None,  # 주유 PER_LITER를 계산하려면 예: 1700 같은 값 필요(모르면 None)
        mile_to_won=0.0,                # 마일 가치 모르면 0 유지(환산에 포함 안 됨)
        point_to_won=1.0
    )
    for r in recs:
        print(r)
