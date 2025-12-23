# card_source/models.py
from django.db import models

class SourceCard(models.Model):
    id = models.IntegerField(primary_key=True)
    gorilla_id = models.IntegerField(null=True, blank=True)

    name = models.TextField(null=True, blank=True)
    company = models.TextField(null=True, blank=True)
    card_type = models.TextField(null=True, blank=True)

    annual_fee = models.TextField(null=True, blank=True)  # TEXT
    min_spending = models.IntegerField(null=True, blank=True)

    image_url = models.TextField(null=True, blank=True)
    local_image_path = models.TextField(null=True, blank=True)

    benefits_summary = models.TextField(null=True, blank=True)
    benefits_json = models.TextField(null=True, blank=True)        # TEXT(JSON)
    structured_benefit = models.TextField(null=True, blank=True)   # TEXT(JSON)

    crawled_at = models.DateTimeField(null=True, blank=True)
    ranking = models.IntegerField(null=True, blank=True)

    class Meta:
        app_label = "card_source"
        managed = False
        db_table = "cards"  # ✅ 여기만 너 원천 테이블명으로 정확히 변경
