import os
import re
import json
import time
import random
import sqlite3
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from openai import OpenAI
import json_repair

# ======================
# 0) Config
# ======================
load_dotenv()

GMS_API_KEY = os.getenv("GMS_KEY")
DB_NAME = os.getenv("DB_NAME", "card_gorilla_master.db")

MODEL = os.getenv("GMS_MODEL", "gpt-4o-mini")
TOP_N = int(os.getenv("TOP_N", "10"))

MAX_INPUT_CHARS = int(os.getenv("MAX_INPUT_CHARS", "2500")) 
MAX_RETRIES = 3
SLEEP_BETWEEN_CALLS = 0.5 
BATCH_COMMIT = 10
TEMPERATURE = 0.0

ALLOWED_CATEGORY = {
    "교통", "통신", "쇼핑", "카페", "음식", "주유", 
    "공과금", "구독", "간편결제", "문화", "여행", "의료", "교육", "기타"
}
ALLOWED_TYPE = {"할인", "적립"}
ALLOWED_UNIT = {"퍼센트", "원", "리터", "마일", "점"}

REQUIRED_KEYS = ("category", "brand", "type", "value", "unit", "limit", "cond")

SYSTEM_PROMPT = """
당신은 카드 혜택 텍스트를 정형화하는 파서입니다.
반드시 스키마에 맞는 JSON 객체만 출력하세요: {"items":[...]}
설명/문장/마크다운/코드펜스 금지.

[필수 규칙]
1. **문맥 준수 (가장 중요)**:
    - 숫자(%, 원, 만원, 천원, 마일, 점, 회) 또는 조건(전월/전년도/건별/통합/한도)이 있는 문장만 근거로 사용.
- '유의사항/제외/산정/수수료/방법/앱 설치/고객센터/예시 날짜' 문장은 무시.
   - "A, B, C" 처럼 쉼표로 브랜드가 나열되면 반드시 A/B/C 각각 별도 아이템을 만든다.
   - 업종만 있고 브랜드가 없으면 brand는 업종명(예: 음식점, 병/의원, 호텔/리조트)으로 1개만 만든다.
   - 특정 브랜드/카테고리의 혜택 값(value)은 반드시 **그 항목의 설명 텍스트 안에 있는 숫자**만 사용해야 합니다.
   - 텍스트 아래쪽에 있는 다른 항목(예: 해외 2%, 구독 50%)의 숫자를 위쪽 항목(음식, 쇼핑)에 갖다 붙이지 마세요.

2. **카테고리(category) 분류 가이드 (엄수)**:
   - **간편결제**: 삼성페이, 네이버페이, 카카오페이, KB Pay 등
   - **음식**: 배달의민족, 요기요, 쿠팡이츠, 음식점
   - **교육**: 학원(입시/보습/예체능), 학습지, 유치원, 어린이집, 학교 납입금, 독서실, 온라인 강의, 등록금
   - **문화**: 영화관(CGV, 롯데시네마 등), 공연, 전시, 도서, 서점
   - **여행**: 항공권, 면세점, 해외 이용, 숙박/호텔, 렌터카, 공항 라운지, 해외
   - **의료**: 병원, 의원, 약국, 동물병원, 산후조리원, 한의원, 대학병원, 치과
   - **교통**: 대중교통, 버스, 지하철, 택시, 기차, KTX, SRT, 카카오T
   - **쇼핑**: 백화점, 마트, 편의점, 온라인쇼핑몰, 아울렛, 다이소, 올리브영, 11번가, G마켓, SSG
   - **구독**: 넷플릭스, 유튜브 프리미엄, 멜론, 쿠팡 와우, 네이버플러스 등 정기 결제
   - **통신**: 이동통신요금, 인터넷/TV 결합상품, SKT, KT, LGU+, 
   - **공과금**: 아파트관리비, 도시가스, 전기세, 4대보험
   - **기타**: 위 분류에 속하지 않는 혜택 (예: 보험, 금융, 자동차 정비 등)

3. **단위(unit) 선택**:
    - 여러 수치가 있으면 가장 큰 수치만 value로 선택 (예: 1~3% -> 3, 주중5/주말10 -> 10)
    - "%": unit="퍼센트"
    - "원/만원/천원": unit="원" (만원/천원은 원으로 환산)
    - "마일": unit="마일"
    - "포인트/점/머니": unit="점"

4. **숫자 추출 및 계산 규칙**:
   - "주중 5%, 주말 10%" 처럼 여러 숫자가 나오면 무조건 가장 큰 숫자(10)를 추출하세요.
   - "최대 5% 적립" -> 5 추출
   - "1,000원당 1마일 적립" -> {"value": 1, "unit": "마일"} (1,000으로 나누지 말고 적립되는 수치만 추출)
   - "100달러(USD) 할인" -> 환율 1,300원 가정하여 환산 -> {"value": 130000, "unit": "원"}
   - 텍스트에 여러 숫자가 섞여 있을 때, **브랜드(brand)에 직접 적용되는 핵심 혜택 숫자**만 추출하세요.

5. **복합 조건 및 선택형 처리**:
   - "주중 5%, 주말 10% 할인"처럼 조건에 따라 숫자가 다르면 **가장 큰 숫자(10)**를 추출하세요.
   - "옵션 1: 커피 5% / 옵션 2: 커피 10%" 처럼 선택형일 경우 '선택형'이라는 제목 대신, **가장 혜택이 큰 옵션**을 기준으로 추출하세요.
   - 텍스트에 여러 숫자가 흩어져 있을 때, 엉뚱한 숫자(예: 해외 2%)를 다른 브랜드(예: 음식점)에 붙이지 않도록 주의하세요.

6. 할인한도(limit) / 실적조건(cond) 추출 규칙:
- "전월 이용금액에 관계없이", "실적 무관", "한도 없이" 문구가 있으면 cond는 0으로 출력
- "전월 이용금액 40만원 이상"처럼 최소 실적이 있으면 cond에 400000을 출력
- "전월실적 30~50 : 3천원 / 50~100 : 7천원 / 100 이상 : 1만원"처럼
  구간별 월 한도가 있으면, 같은 혜택을 구간별로 여러 JSON 객체로 출력
  (각 객체는 cond=구간 하한, limit=해당 구간 월 한도)
- "통합 월 할인한도 5,000원"이면 limit=5000으로 출력

[cond / limit]
- cond: "전월 이용금액 N원 이상"의 N(원). 실적 무관/조건 없음이면 0.
- limit: "통합 월/연/건당 한도" 금액(원). 없으면 0.
- "구간별 한도"가 있으면 구간별로 아이템을 여러 개로 분리 (cond=구간 하한, limit=해당 한도).

[입력 예시]
- 대한항공: 1,000원당 1마일 적립
- 학원: 예체능 학원 10% 할인 (월 한도 1만원)
- 커피: 스타벅스 50% 할인
- 음식: 주중 5%, 주말 10% 할인
- 구독: 넷플릭스 50% 할인
- 해외: 2% 할인
- 공과금 10% 할인
  전월실적 30~50: 3천원 / 50~100: 7천원 / 100 이상: 1만원

[출력 예시]
[
  {"category":"여행","brand":"대한항공","type":"적립","value":1,"unit":"마일","limit":0,"cond":0},
  {"category":"교육","brand":"학원","type":"할인","value":10,"unit":"퍼센트","limit":10000,"cond":0},
  {"category":"카페","brand":"스타벅스","type":"할인","value":50,"unit":"퍼센트","limit":0,"cond":0},
  {"category":"음식","brand":"음식점","type":"할인","value":10,"unit":"퍼센트","limit":0,"cond":0},
  {"category":"구독","brand":"넷플릭스","type":"할인","value":50,"unit":"퍼센트","limit":0,"cond":0},
  {"category":"여행","brand":"해외","type":"할인","value":2,"unit":"퍼센트","limit":0,"cond":0},
  {"category":"공과금","brand":"공과금","type":"할인","value":10,"unit":"퍼센트","limit":3000,"cond":300000},
  {"category":"공과금","brand":"공과금","type":"할인","value":10,"unit":"퍼센트","limit":7000,"cond":500000},
  {"category":"공과금","brand":"공과금","type":"할인","value":10,"unit":"퍼센트","limit":10000,"cond":1000000}
]


반드시 {"items":[{category,brand,type,value,unit,limit,cond}, ...]} 형태로만 출력.
""".strip()


# ======================
# 0-1) Structured Outputs: JSON Schema & Tools
# ======================
# 스키마는 "items" 래퍼를 씌워서 (일부 환경에서 최상위 array보다 호환성이 좋아서) 사용
BENEFIT_ITEM_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "category": {"type": "string", "enum": sorted(ALLOWED_CATEGORY)},
        "brand": {"type": "string"},
        "type": {"type": "string", "enum": sorted(ALLOWED_TYPE)},
        "value": {"type": "number"},
        "unit": {"type": "string", "enum": sorted(ALLOWED_UNIT)},
        "limit": {"type": "integer"},
        "cond": {"type": "integer"},
    },
    # cond는 누락 가능 (추후 누락 시 카드 min_spending으로 보정)
    "required": ["category", "brand", "type", "value", "unit", "limit"],
}

BENEFITS_WRAPPER_SCHEMA: Dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "items": {
            "type": "array",
            "maxItems": 120,
            "items": BENEFIT_ITEM_SCHEMA,
        }
    },
    "required": ["items"],
}

# Responses API의 text.format(json_schema)용
TEXT_FORMAT_JSON_SCHEMA: Dict[str, Any] = {
    "type": "json_schema",
    "name": "card_benefits",
    "strict": True,
    "schema": BENEFITS_WRAPPER_SCHEMA,
}

# Tool calling용 (Chat Completions API)
TOOLS_CHAT_COMPLETIONS = [
    {
        "type": "function",
        "function": {
            "name": "extract_benefits",
            "description": "Parse card benefit text into normalized benefit items.",
            "parameters": BENEFITS_WRAPPER_SCHEMA,
        },
    }
]


# ======================
# 1) Helpers
# ======================
def get_client() -> OpenAI:
    if not GMS_API_KEY:
        print("⚠️ 경고: GMS_KEY가 환경 변수에 없습니다.")
    return OpenAI(api_key=GMS_API_KEY, base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1")


def has_column(conn: sqlite3.Connection, table: str, col: str) -> bool:
    cur = conn.cursor()
    cur.execute(f"PRAGMA table_info({table})")
    return any(r[1] == col for r in cur.fetchall())


def ensure_structured_benefit_column(conn: sqlite3.Connection) -> None:
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='cards'")
    if cur.fetchone()[0] == 0:
        print("❌ 'cards' 테이블이 없습니다.")
        return

    columns_to_add = {
        "structured_benefit": "TEXT",
        "structured_benefit_raw": "TEXT",
        "structured_benefit_error": "TEXT",
    }

    for col, col_type in columns_to_add.items():
        if not has_column(conn, "cards", col):
            cur.execute(f"ALTER TABLE cards ADD COLUMN {col} {col_type}")
            conn.commit()
            print(f"✅ '{col}' 컬럼 생성 완료")


def strip_code_fence(s: str) -> str:
    s = (s or "").strip()
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

    # 예: "1만원", "30만", "5천원", "2.5만 원"
    m = re.search(r"([-+]?\d+(?:\.\d+)?)\s*(만|천|백)?\s*원?", s)
    if m:
        num = float(m.group(1))
        unit = m.group(2)
        factor = {"만": 10000, "천": 1000, "백": 100}.get(unit, 1)
        return int(round(num * factor))

    return int(round(to_scalar(s)))


def normalize_item(item: Dict[str, Any], card_level_min_spending: int) -> Dict[str, Any]:
    out: Dict[str, Any] = {k: item.get(k) for k in REQUIRED_KEYS}

    cat = str(out.get("category") or "기타").strip()
    out["category"] = cat if cat in ALLOWED_CATEGORY else "기타"

    out["brand"] = str(out.get("brand") or "ALL").strip()

    t = str(out.get("type") or "할인").strip()
    out["type"] = t if t in ALLOWED_TYPE else "할인"

    unit = str(out.get("unit") or "원").strip()
    out["unit"] = unit if unit in ALLOWED_UNIT else "원"

    if out["unit"] == "원":
        out["value"] = to_won(out.get("value"))
    else:
        out["value"] = to_scalar(out.get("value"))

    out["limit"] = to_won(out.get("limit"))

    raw_cond = item.get("cond", None)
    if raw_cond is None or (isinstance(raw_cond, str) and raw_cond.strip() == ""):
        out["cond"] = to_won(card_level_min_spending)
    else:
        out["cond"] = to_won(raw_cond)  # 0 / "0" 그대로 인정

    return out


def parse_any_json_to_items(raw: str) -> List[Dict[str, Any]]:
    """
    raw JSON이
    - {"items":[...]} 이거나
    - [...] 이거나
    - {...} 이거나
    무엇이든 items(list[dict])로 정규화해서 반환
    """
    raw = strip_code_fence(raw)

    try:
        data = json_repair.loads(raw)
    except Exception:
        return []

    # {"items":[...]} 래퍼 지원
    if isinstance(data, dict) and "items" in data and isinstance(data["items"], list):
        data = data["items"]

    if isinstance(data, dict):
        data = [data]

    if not isinstance(data, list):
        return []

    return [x for x in data if isinstance(x, dict)]


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
        if any(k in title for k in ["유의사항", "꼭 확인", "꼭 확인하세요", "안내사항", "주의사항", "참고사항", "참고", "전월 이용금액 기준", "전년도 이용금액 기준", "전월 이용금액 제외", "전년도 이용금액 제외", "할인 제외 대상", "적립 제외 대상"]):
            continue

        summary = str(item.get("summary", "")).strip()
        detail = str(item.get("detail", "")).strip()

        content_parts: List[str] = []
        if detail:
            content_parts.append(detail)
        elif summary:
            content_parts.append(summary)

        content = "\n".join(content_parts).strip()
        content = compact_detail(content)
        if not title and not content:
            continue

        lines.append(f"- {title}: {content}")

    if not lines:
        return None

    text = "\n".join(lines)
    return text[:max_chars]

CUT_RE = re.compile(
    r"(전월 이용금액 기준|전년도 이용금액 기준|전월 이용금액 제외|전년도 이용금액 제외|"
    r"할인 제외 대상|적립 제외 대상|전년도 이용금액 제외 대상|전월 이용금액 제외 대상|"
    r"유의사항|안내사항)",
    re.MULTILINE
)

def compact_detail(s: str, max_lines: int = 120) -> str:
    s = (s or "").replace("\r", "")
    # HTML 엔티티 간단 제거 (&rarr; 등)
    s = re.sub(r"&[^;\s]+;", " ", s)

    # 유의/제외/산정 이후는 통째로 잘라내기
    parts = CUT_RE.split(s)
    if parts:
        s = parts[0]

    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    kept: List[str] = []

    # 숫자/조건/브랜드 라인만 남기기 (정밀 추출에 필요한 것 위주)
    for ln in lines:
        if re.search(r"(\d|%|원|만원|천원|마일|점|회|이상|미만|한도|통합|건별|전월|전년도)", ln):
            kept.append(ln)
        elif "," in ln:
            kept.append(ln[:400]) 

        if len(kept) >= max_lines:
            break

    return "\n".join(kept)


def call_llm_structured_with_retry(client: OpenAI, text: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    반환:
      raw_str: 모델 원문(가능하면)
      items: list[dict] (정규화 전)
    """
    last_err: Optional[Exception] = None

    for attempt in range(1, MAX_RETRIES + 1):
        # 1) Responses API + text.format(json_schema) (가능하면 최우선)
        try:
            resp = client.responses.create(
                model=MODEL,
                input=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": text},
                ],
                text={"format": TEXT_FORMAT_JSON_SCHEMA},
                temperature=TEMPERATURE,
            )
            raw = (getattr(resp, "output_text", "") or "").strip()
            items = parse_any_json_to_items(raw)
            return raw, items
        except Exception as e:
            last_err = e

        # 2) Chat Completions API + tool calling (fallback)
        try:
            resp2 = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {
                        "role": "user",
                        "content": (
                            "아래 텍스트에서 혜택을 추출해서 extract_benefits 함수를 호출하세요.\n\n"
                            + text
                        ),
                    },
                ],
                tools=TOOLS_CHAT_COMPLETIONS,
                tool_choice={"type": "function", "function": {"name": "extract_benefits"}},
                temperature=TEMPERATURE,
            )

            msg = resp2.choices[0].message
            tool_calls = getattr(msg, "tool_calls", None) or []

            if tool_calls:
                args_str = tool_calls[0].function.arguments or ""
                items = parse_any_json_to_items(args_str)
                # tool call args 자체를 raw로 저장
                return args_str.strip(), items

            # tool call이 안 왔으면 content를 raw로 삼고 마지막 fallback 파싱
            raw = (msg.content or "").strip()
            items = parse_any_json_to_items(raw)
            return raw, items
        except Exception as e:
            last_err = e

        print(f"  Warning: LLM call failed (attempt {attempt})... ({last_err})")
        time.sleep((1 * attempt) + random.uniform(0, 1))

    raise RuntimeError(f"LLM 호출 실패: {last_err}")


# ======================
# 2) Main
# ======================
def refine_top_cards() -> None:
    client = get_client()

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    try:
        ensure_structured_benefit_column(conn)

        ranking_exists = has_column(conn, "cards", "ranking")

        query = """
            SELECT gorilla_id, name, benefits_json, min_spending
            FROM cards
            WHERE (structured_benefit IS NULL OR structured_benefit = '')
        """
        params: List[Any] = []

        if ranking_exists:
            query += " AND ranking IS NOT NULL AND ranking <= ? ORDER BY ranking ASC LIMIT ?"
            params = [TOP_N, TOP_N]
        else:
            query += " LIMIT ?"
            params = [TOP_N]

        cursor.execute(query, params)
        cards = cursor.fetchall()
        print(f"🤖 LLM으로 카드 {len(cards)}개 분석 시작")

        ok = 0
        fail = 0
        pending = 0

        for idx, row in enumerate(cards, start=1):
            g_id = row["gorilla_id"]
            name = row["name"]
            benefits_json_str = row["benefits_json"]
            card_min_spending = to_won(row["min_spending"])

            text = build_input_text(benefits_json_str, MAX_INPUT_CHARS)
            if not text:
                print(f"[{idx}] {name}: 혜택 데이터 없음 (Skip)")
                # 실패로 보고 error 남길지 정책 선택 가능
                update_cur = conn.cursor()
                update_cur.execute(
                    "UPDATE cards SET structured_benefit_error = ?, structured_benefit_raw = ? WHERE gorilla_id = ?",
                    ("혜택 데이터 없음 (Skip)", "", g_id),
                )
                fail += 1
                continue

            print(f"[{idx}] {name} 분석 중...", end=" ", flush=True)

            raw = ""  # ✅ 실패 시에도 raw 저장하기 위해 바깥에 둠
            try:
                raw, items = call_llm_structured_with_retry(client, text)

                # items 정규화
                normalized: List[Dict[str, Any]] = []
                MAX_OUTPUT_ITEMS = 120  # 스키마와 맞추기

                for x in items[:MAX_OUTPUT_ITEMS]:
                    if isinstance(x, dict):
                        normalized.append(normalize_item(x, card_min_spending))

                if not normalized:
                    update_cur = conn.cursor()
                    update_cur.execute(
                        """
                        UPDATE cards
                        SET structured_benefit_raw = ?,
                            structured_benefit_error = ?
                        WHERE gorilla_id = ?
                        """,
                        (raw, "결과 없음 (Empty)", g_id),
                    )
                    print("결과 없음 (Empty) ⚠️")
                    fail += 1
                    continue

                json_str_db = json.dumps(normalized, ensure_ascii=False, separators=(",", ":"))

                update_cur = conn.cursor()
                update_cur.execute(
                    """
                    UPDATE cards
                    SET structured_benefit = ?,
                        structured_benefit_raw = ?,
                        structured_benefit_error = NULL
                    WHERE gorilla_id = ?
                    """,
                    (json_str_db, raw, g_id),
                )

                ok += 1
                pending += 1
                print(f"성공 ({len(normalized)}개 추출) ✅")

                if pending >= BATCH_COMMIT:
                    conn.commit()
                    pending = 0

            except Exception as e:
                fail += 1
                error_message = f"{e}"
                print(f"실패 ❌: {error_message}")

                # ✅ 실패 시에도 structured_benefit_raw를 같이 저장
                update_cur = conn.cursor()
                update_cur.execute(
                    """
                    UPDATE cards
                    SET structured_benefit_error = ?,
                        structured_benefit_raw = ?
                    WHERE gorilla_id = ?
                    """,
                    (error_message, raw or "", g_id),
                )

            time.sleep(SLEEP_BETWEEN_CALLS + random.uniform(0, 0.5))

        if pending > 0:
            conn.commit()

        print(f"\n🎉 완료: 성공={ok}, 실패={fail}, 총 대상={len(cards)}")

    finally:
        conn.close()


if __name__ == "__main__":
    refine_top_cards()