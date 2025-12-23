# recommend/models.py
from django.db import models

class CardBenefitIndex(models.Model):
    source_card_id = models.IntegerField(db_index=True)   # SourceCard.id

    category = models.CharField(max_length=30, db_index=True)  # COFFEE/FOOD/TRANS...
    benefit_type = models.CharField(max_length=20, blank=True, default="PERCENT")

    rate = models.FloatField(null=True, blank=True)       # 0.05
    amount_won = models.IntegerField(null=True, blank=True)
    limit_month_won = models.IntegerField(null=True, blank=True)

    title = models.CharField(max_length=255, blank=True, default="")
    desc = models.TextField(blank=True, default="")
    cond_min_spending = models.IntegerField(null=True, blank=True)
    brand = models.CharField(max_length=50, blank=True, default="ALL")
    raw_type = models.CharField(max_length=30, blank=True, default="")

    class Meta:
        indexes = [
            models.Index(fields=["source_card_id", "category"]),
        ]
