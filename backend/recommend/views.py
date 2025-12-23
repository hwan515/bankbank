from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from cards.models import UserProfile  # 너 프로젝트에 이미 있음
from card_source.models import SourceCard

from recommend.services.repository import fetch_benefit_rows
from recommend.services.scoring import rank_cards_by_profile


class RecommendCardsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from cards.models import UserProfile

        profile, _ = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={
                "monthly_spend": 500000,          # 기본값(원하는 값으로)
                "category_weights": {"FOOD": 1, "COFFEE": 1, "TRANS": 1},
                "fee_tolerance": 20000,
                "min_spend_tolerance": 300000,
            },
        )

        category_weights = profile.category_weights or {}
        monthly_spend = int(profile.monthly_spend or 0)
        min_spend_tolerance = getattr(profile, "min_spend_tolerance", None)

        categories = set(category_weights.keys()) | {"ALL"}  # ALL 혜택도 반영할 거면 포함
        benefit_rows = fetch_benefit_rows(categories)

        ranked = rank_cards_by_profile(
            benefit_rows=benefit_rows,
            category_weights=category_weights,
            monthly_spend=monthly_spend,
            min_spend_tolerance=min_spend_tolerance,
            all_weight=0.3,
            top_n=10,
        )

        ids = [cid for cid, _ in ranked]

        # 원천 카드 정보는 card_source DB에서 조회
        cards = SourceCard.objects.using("card_source").filter(id__in=ids)
        card_map = {c.id: c for c in cards}

        results = []
        for cid, score in ranked:
            c = card_map.get(cid)
            if not c:
                continue
            results.append({
                "id": c.id,
                "name": c.name,
                "company": c.company,
                "image_url": c.image_url,
                "annual_fee": c.annual_fee,
                "min_spending": c.min_spending,
                "ranking": c.ranking,
                "score": round(score, 2),
            })

        return Response({"results": results})
