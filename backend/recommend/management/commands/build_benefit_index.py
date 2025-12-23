from django.core.management.base import BaseCommand
from django.db import transaction

from card_source.models import SourceCard
from recommend.models import CardBenefitIndex
from recommend.services.etl import safe_json_loads, normalize_one_benefit

class Command(BaseCommand):
    help = "card_source DB의 SourceCard.structured_benefit를 펼쳐 CardBenefitIndex를 생성"

    def add_arguments(self, parser):
        parser.add_argument("--truncate", action="store_true")

    @transaction.atomic
    def handle(self, *args, **opts):
        if opts["truncate"]:
            CardBenefitIndex.objects.all().delete()

        bulk = []
        qs = SourceCard.objects.using("card_source").all()

        for c in qs.iterator(chunk_size=500):
            benefits = safe_json_loads(c.structured_benefit) or []
            if isinstance(benefits, dict):
                # 혹시 {"benefits":[...]} 형태면
                benefits = benefits.get("benefits", [])
            if not isinstance(benefits, list):
                continue

            for b in benefits:
                if not isinstance(b, dict):
                    continue
                row = normalize_one_benefit(b)

                # percent든 won이든 일단 저장
                if row["benefit_type"] == "UNKNOWN":
                    continue

                bulk.append(CardBenefitIndex(
                    source_card_id=c.id,
                    category=row["category"],
                    title=row["title"],
                    desc=row["desc"],
                    rate=row["rate"],
                    amount_won=row["amount_won"],
                    limit_month_won=row["limit_month_won"],
                    benefit_type=row["benefit_type"],
                    cond_min_spending=row.get("cond"),
                    brand=row.get("brand") or "ALL",
                    raw_type=row.get("raw_type") or "",
                ))


        CardBenefitIndex.objects.bulk_create(bulk, batch_size=2000)
        self.stdout.write(self.style.SUCCESS(f"✅ CardBenefitIndex 적재 완료: {len(bulk)} rows"))
