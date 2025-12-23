from recommend.models import CardBenefitIndex

def fetch_benefit_rows(categories: set[str]):
    return list(
        CardBenefitIndex.objects.filter(category__in=list(categories)).values(
            "source_card_id",
            "category",
            "rate",
            "amount_won",
            "limit_month_won",
            "cond_min_spending",
        )
    )
