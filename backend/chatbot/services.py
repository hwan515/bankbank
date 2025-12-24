import json
import logging
import os
from typing import Any, Dict, List, Optional, Tuple

from django.db.models import F, OuterRef, Subquery

from openai import OpenAI

from cards.models import Card, UserProfile
from cards.serializers import CardListSerializer
from cards.services.recommend import CardRecommendService
from products.models import (
    DepositOptions,
    DepositProducts,
    DepositSubscription,
    SavingOptions,
    SavingProducts,
    SavingSubscription,
)
from products.serializers import DepositProductsListSerializer, SavingProductsListSerializer

logger = logging.getLogger(__name__)

GMS_BASE_URL = os.getenv("GMS_BASE_URL", "https://gms.ssafy.io/gmsapi/api.openai.com/v1")
DEFAULT_K = 5
MAX_K = 10

SYSTEM_PROMPT = (
    "당신은 금융상품/카드 추천을 돕는 챗봇입니다. "
    "사용자가 카드 추천/비교를 요청하면 recommend_cards 도구를 호출하세요. "
    "예금 상품은 search_deposit_products, 적금 상품은 search_saving_products 도구를 호출하세요. "
    "사용자가 자신이 가입한 상품, 내 상품, 내 예금/적금 등을 물어보면 get_my_subscriptions 도구를 호출하세요. "
    "도구 결과가 제공되면 해당 데이터만 근거로 답하고, "
    "데이터가 없으면 간단히 알려준 뒤 자세한 조건을 질문하세요. "
    "마크다운/별표 강조 없이 순수 텍스트로 답변하세요. "
    "한국어로 간결하게 답변하세요."
)


TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "recommend_cards",
            "description": "자연어 질의와 조건을 기반으로 카드 추천 결과를 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "k": {"type": "integer", "minimum": 1, "maximum": 10},
                    "filters": {
                        "type": "object",
                        "properties": {
                            "company": {"type": "string"},
                            "card_type": {"type": "string", "description": "CRD 또는 CHK"},
                            "max_annual_fee": {"type": "integer"},
                            "max_min_spending": {"type": "integer"},
                        },
                    },
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_deposit_products",
            "description": "정기예금 상품을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bank": {"type": "string", "description": "은행명"},
                    "search": {"type": "string", "description": "상품명 검색어"},
                    "term_months": {"type": "integer", "description": "6/12/24/36개월 중 하나"},
                    "k": {"type": "integer", "minimum": 1, "maximum": 10},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_saving_products",
            "description": "적금 상품을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "bank": {"type": "string", "description": "은행명"},
                    "search": {"type": "string", "description": "상품명 검색어"},
                    "term_months": {"type": "integer", "description": "6/12/24/36개월 중 하나"},
                    "k": {"type": "integer", "minimum": 1, "maximum": 10},
                },
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_my_subscriptions",
            "description": "현재 로그인한 사용자가 가입한 예금/적금 상품 목록을 조회합니다.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_type": {
                        "type": "string",
                        "description": "조회할 상품 유형: deposit(예금), saving(적금), all(전체). 기본값은 all",
                        "enum": ["deposit", "saving", "all"],
                    },
                },
            },
        },
    },
]


class GmsChatbotService:
    def __init__(self) -> None:
        self.api_key = os.getenv("GMS_KEY", "")
        self.model = os.getenv("GMS_MODEL", "gpt-4o-mini")
        self.client = OpenAI(api_key=self.api_key, base_url=GMS_BASE_URL)
        self.card_service = CardRecommendService()

    def handle_message(self, user, message: str) -> Dict[str, Any]:
        cards_payload: List[Dict[str, Any]] = []
        products_payload: Dict[str, List[Dict[str, Any]]] = {
            "deposits": [],
            "savings": [],
            "my_deposits": [],
            "my_savings": [],
        }

        if not self.api_key:
            return {
                "reply": "현재 챗봇 설정이 준비되지 않았어요. 관리자에게 문의해 주세요.",
                "cards": cards_payload,
                "products": products_payload,
            }

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": message},
        ]

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",
                temperature=0.3,
            )
        except Exception as e:
            logger.error(f"OpenAI API 호출 실패: {e}", exc_info=True)
            return {
                "reply": "지금은 챗봇 응답을 생성할 수 없어요. 잠시 후 다시 시도해 주세요.",
                "cards": cards_payload,
                "products": products_payload,
            }

        assistant_message = response.choices[0].message
        tool_calls = getattr(assistant_message, "tool_calls", None) or []

        if tool_calls:
            messages.append(assistant_message)
            for tool_call in tool_calls:
                name = tool_call.function.name
                args = self._parse_tool_args(tool_call.function.arguments or "")
                try:
                    if name == "recommend_cards":
                        tool_result, cards_payload = self._handle_recommend_cards(
                            user=user,
                            message=message,
                            args=args,
                        )
                    elif name == "search_deposit_products":
                        tool_result, products_payload["deposits"] = self._handle_deposit_search(args)
                    elif name == "search_saving_products":
                        tool_result, products_payload["savings"] = self._handle_saving_search(args)
                    elif name == "get_my_subscriptions":
                        tool_result, subscriptions = self._handle_my_subscriptions(user, args)
                        products_payload["my_deposits"] = subscriptions.get("deposits", [])
                        products_payload["my_savings"] = subscriptions.get("savings", [])
                    else:
                        tool_result = {"error": f"unknown_tool:{name}"}
                except Exception as e:
                    logger.warning(f"Tool 실행 실패 ({name}): {e}", exc_info=True)
                    tool_result = {"error": f"tool_failed:{name}"}

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(tool_result, ensure_ascii=False),
                    }
                )

            try:
                final = self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.3,
                )
                reply = (final.choices[0].message.content or "").strip()
            except Exception as e:
                logger.warning(f"최종 응답 생성 실패: {e}", exc_info=True)
                reply = ""
        else:
            reply = (assistant_message.content or "").strip()

        reply = self._strip_markdown(reply)

        if not reply:
            reply = "원하시는 조건을 조금 더 알려주실 수 있을까요?"

        return {
            "reply": reply,
            "cards": cards_payload,
            "products": products_payload,
        }

    def _handle_recommend_cards(
        self,
        user,
        message: str,
        args: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        query = (args.get("query") or message or "").strip()
        k = self._clamp_k(args.get("k"))
        raw_filters = args.get("filters") or {}
        filters = self._normalize_card_filters(raw_filters)
        filters = self._apply_user_profile(user, filters)

        hits = self.card_service.recommend(query=query, k=k, filters=filters)
        cards_payload = self._serialize_card_hits(hits)
        tool_result = {
            "count": len(cards_payload),
            "cards": [
                {
                    "name": item["card"]["name"],
                    "company": item["card"]["company"],
                    "annual_fee_min": item["card"]["annual_fee_min"],
                    "min_spending": item["card"]["min_spending"],
                    "reasons": item["reasons"],
                }
                for item in cards_payload
            ],
        }

        return tool_result, cards_payload

    def _handle_deposit_search(
        self,
        args: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        bank = (args.get("bank") or "").strip()
        search = (args.get("search") or "").strip()
        term_months = self._normalize_term(args.get("term_months"))
        k = self._clamp_k(args.get("k"))

        products = self._query_deposit_products(bank, search, term_months, k)
        tool_result = {
            "count": len(products),
            "products": self._summarize_products(products, term_months),
        }
        return tool_result, products

    def _handle_saving_search(
        self,
        args: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        bank = (args.get("bank") or "").strip()
        search = (args.get("search") or "").strip()
        term_months = self._normalize_term(args.get("term_months"))
        k = self._clamp_k(args.get("k"))

        products = self._query_saving_products(bank, search, term_months, k)
        tool_result = {
            "count": len(products),
            "products": self._summarize_products(products, term_months),
        }
        return tool_result, products

    def _handle_my_subscriptions(
        self,
        user,
        args: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Dict[str, List[Dict[str, Any]]]]:
        if not getattr(user, "is_authenticated", False):
            return {"error": "로그인이 필요합니다."}, {"deposits": [], "savings": []}

        product_type = (args.get("product_type") or "all").strip().lower()

        deposits: List[Dict[str, Any]] = []
        savings: List[Dict[str, Any]] = []

        if product_type in ("deposit", "all"):
            deposit_subs = DepositSubscription.objects.filter(user=user).select_related("product")
            for sub in deposit_subs:
                product = sub.product
                rate = self._get_deposit_rate(product, sub.term_months)
                deposits.append({
                    "id": product.id,
                    "fin_prdt_cd": product.fin_prdt_cd,
                    "fin_prdt_nm": product.fin_prdt_nm,
                    "kor_co_nm": product.kor_co_nm,
                    "term_months": sub.term_months,
                    "rate": rate,
                    "subscribed_at": sub.created_at.isoformat() if sub.created_at else None,
                })

        if product_type in ("saving", "all"):
            saving_subs = SavingSubscription.objects.filter(user=user).select_related("product")
            for sub in saving_subs:
                product = sub.product
                rate = self._get_saving_rate(product, sub.term_months)
                savings.append({
                    "id": product.id,
                    "fin_prdt_cd": product.fin_prdt_cd,
                    "fin_prdt_nm": product.fin_prdt_nm,
                    "kor_co_nm": product.kor_co_nm,
                    "term_months": sub.term_months,
                    "rsrv_type": sub.rsrv_type,
                    "monthly_amount": sub.monthly_amount,
                    "rate": rate,
                    "subscribed_at": sub.created_at.isoformat() if sub.created_at else None,
                })

        tool_result = {
            "deposit_count": len(deposits),
            "saving_count": len(savings),
            "deposits": [
                {
                    "name": d["fin_prdt_nm"],
                    "bank": d["kor_co_nm"],
                    "term_months": d["term_months"],
                    "rate": d["rate"],
                }
                for d in deposits
            ],
            "savings": [
                {
                    "name": s["fin_prdt_nm"],
                    "bank": s["kor_co_nm"],
                    "term_months": s["term_months"],
                    "rate": s["rate"],
                    "monthly_amount": s["monthly_amount"],
                }
                for s in savings
            ],
        }

        return tool_result, {"deposits": deposits, "savings": savings}

    def _get_deposit_rate(self, product, term_months: Optional[int]):
        if term_months is None:
            term_months = 12
        option = DepositOptions.objects.filter(
            product=product, save_trm=term_months
        ).order_by("-intr_rate2").first()
        if option:
            return float(option.intr_rate2) if option.intr_rate2 else None
        return None

    def _get_saving_rate(self, product, term_months: Optional[int]):
        if term_months is None:
            term_months = 12
        option = SavingOptions.objects.filter(
            product=product, save_trm=term_months
        ).order_by("-intr_rate2").first()
        if option:
            return float(option.intr_rate2) if option.intr_rate2 else None
        return None

    def _parse_tool_args(self, raw: str) -> Dict[str, Any]:
        raw = raw.strip()
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {}

    def _clamp_k(self, value: Optional[Any]) -> int:
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            parsed = DEFAULT_K
        return max(1, min(MAX_K, parsed))

    def _normalize_term(self, value: Optional[Any]) -> Optional[int]:
        try:
            term = int(value)
        except (TypeError, ValueError):
            return None
        return term if term in (6, 12, 24, 36) else None

    def _normalize_card_filters(self, filters: Dict[str, Any]) -> Dict[str, Any]:
        normalized: Dict[str, Any] = {}

        company = (filters.get("company") or "").strip()
        if company:
            normalized["company"] = company

        card_type = (filters.get("card_type") or "").strip()
        if card_type:
            upper = card_type.upper()
            if upper in ("CRD", "CHK"):
                normalized["card_type"] = upper
            elif "체크" in card_type:
                normalized["card_type"] = "CHK"
            elif "신용" in card_type:
                normalized["card_type"] = "CRD"

        max_annual_fee = self._to_int(filters.get("max_annual_fee"))
        if max_annual_fee is not None:
            normalized["max_annual_fee"] = max_annual_fee

        max_min_spending = self._to_int(filters.get("max_min_spending"))
        if max_min_spending is not None:
            normalized["max_min_spending"] = max_min_spending

        return normalized

    def _apply_user_profile(self, user, filters: Dict[str, Any]) -> Dict[str, Any]:
        if not getattr(user, "is_authenticated", False):
            return filters

        try:
            profile = UserProfile.objects.get(user=user)
        except UserProfile.DoesNotExist:
            return filters

        updated = dict(filters)
        if profile.category_weights and "category_weights" not in updated:
            updated["category_weights"] = profile.category_weights
        if profile.fee_tolerance is not None and "max_annual_fee" not in updated:
            updated["max_annual_fee"] = int(profile.fee_tolerance)
        if profile.min_spend_tolerance is not None and "max_min_spending" not in updated:
            updated["max_min_spending"] = int(profile.min_spend_tolerance)
        return updated

    def _serialize_card_hits(self, hits) -> List[Dict[str, Any]]:
        gids = [hit.gorilla_id for hit in hits]
        if not gids:
            return []

        cards = Card.objects.filter(gorilla_id__in=gids)
        card_map = {card.gorilla_id: card for card in cards}
        results = []
        for hit in hits:
            card = card_map.get(hit.gorilla_id)
            if not card:
                continue
            results.append(
                {
                    "card": CardListSerializer(card).data,
                    "score": round(float(hit.score), 4),
                    "reasons": hit.reasons,
                    "preview": hit.preview,
                }
            )
        return results

    def _query_deposit_products(
        self, bank: str, search: str, term_months: Optional[int], k: int
    ) -> List[Dict[str, Any]]:
        products = DepositProducts.objects.all()
        products = self._annotate_deposit_rates(products)
        if bank:
            products = products.filter(kor_co_nm__icontains=bank)
        if search:
            products = products.filter(fin_prdt_nm__icontains=search)

        ordering = self._term_ordering(term_months)
        products = products.order_by(F(ordering).desc(nulls_last=True))
        return DepositProductsListSerializer(list(products[:k]), many=True).data

    def _query_saving_products(
        self, bank: str, search: str, term_months: Optional[int], k: int
    ) -> List[Dict[str, Any]]:
        products = SavingProducts.objects.all()
        products = self._annotate_saving_rates(products)
        if bank:
            products = products.filter(kor_co_nm__icontains=bank)
        if search:
            products = products.filter(fin_prdt_nm__icontains=search)

        ordering = self._term_ordering(term_months)
        products = products.order_by(F(ordering).desc(nulls_last=True))
        return SavingProductsListSerializer(list(products[:k]), many=True).data

    def _annotate_deposit_rates(self, qs):
        rate_subqueries = {}
        for term in (6, 12, 24, 36):
            rate_subqueries[f"intr_rate_{term}"] = Subquery(
                DepositOptions.objects.filter(
                    product=OuterRef("pk"),
                    save_trm=term,
                )
                .order_by("-intr_rate2")
                .values("intr_rate2")[:1]
            )
        return qs.annotate(**rate_subqueries)

    def _annotate_saving_rates(self, qs):
        rate_subqueries = {}
        for term in (6, 12, 24, 36):
            rate_subqueries[f"intr_rate_{term}"] = Subquery(
                SavingOptions.objects.filter(
                    product=OuterRef("pk"),
                    save_trm=term,
                )
                .order_by("-intr_rate2")
                .values("intr_rate2")[:1]
            )
        return qs.annotate(**rate_subqueries)

    def _term_ordering(self, term_months: Optional[int]) -> str:
        if term_months in (6, 12, 24, 36):
            return f"intr_rate_{term_months}"
        return "intr_rate_12"

    def _summarize_products(
        self, products: List[Dict[str, Any]], term_months: Optional[int]
    ) -> List[Dict[str, Any]]:
        summaries = []
        for item in products:
            rate = self._pick_rate(item, term_months)
            summaries.append(
                {
                    "name": item.get("fin_prdt_nm"),
                    "bank": item.get("kor_co_nm"),
                    "rate": rate,
                    "term_months": term_months,
                }
            )
        return summaries

    def _strip_markdown(self, text: str) -> str:
        if not text:
            return ""
        cleaned = text.replace("**", "").replace("__", "")
        return cleaned.strip()

    def _pick_rate(self, item: Dict[str, Any], term_months: Optional[int]):
        if term_months in (6, 12, 24, 36):
            return item.get(f"intr_rate_{term_months}")

        for key in ("intr_rate_12", "intr_rate_24", "intr_rate_6", "intr_rate_36"):
            rate = item.get(key)
            if rate is not None:
                return rate
        return None

    def _to_int(self, value: Optional[Any]) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
