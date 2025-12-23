from collections import defaultdict

def rank_cards_by_profile(
    benefit_rows: list[dict],
    category_weights: dict,
    monthly_spend: int,
    min_spend_tolerance: int | None = None,
    all_weight: float = 0.3,
    top_n: int = 10,
):
    """
    benefit_rows: CardBenefitIndex.values(...) 리스트
    category_weights: {"COFFEE": 0.2, "FOOD": 0.4, ...}
    monthly_spend: 월 사용액 (원)
    min_spend_tolerance: 유저가 감당 가능한 전월실적(원) (없으면 cond 무시)
    """
    w = {k: float(v) for k, v in (category_weights or {}).items() if v is not None and float(v) > 0}
    if not w or monthly_spend <= 0:
        return []

    w_sum = sum(w.values())
    scores = defaultdict(float)

    for b in benefit_rows:
        card_id = b["source_card_id"]
        cat = b["category"]

        # cond(전월실적 조건) 필터
        cond = b.get("cond_min_spending")
        if min_spend_tolerance is not None and cond is not None:
            if int(min_spend_tolerance) < int(cond):
                continue

        # base spend 배분
        if cat == "ALL":
            base = float(monthly_spend) * float(all_weight)
        else:
            base = float(monthly_spend) * (w.get(cat, 0.0) / w_sum)

        # 할인 계산: percent 우선
        disc = 0.0
        rate = b.get("rate")
        amount_won = b.get("amount_won")

        if rate is not None:
            disc = base * float(rate)
        elif amount_won is not None:
            disc = float(amount_won)

        # 월한도
        limit_month = b.get("limit_month_won")
        if limit_month is not None:
            disc = min(disc, float(limit_month))

        scores[card_id] += disc

    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return ranked
