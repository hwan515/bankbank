from django.contrib import admin
from .models import Card, UserProfile, UserEvent, RecommendationLog, CardEmbeddingState


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ['id', 'gorilla_id', 'name', 'company', 'card_type', 'primary_category', 'ranking', 'annual_fee_min', 'min_spending']
    list_filter = ['company', 'card_type']
    search_fields = ['name', 'company', 'benefits_summary']
    ordering = ['ranking', '-created_at']
    readonly_fields = ['created_at', 'updated_at', 'crawled_at']

    fieldsets = (
        ('기본 정보', {
            'fields': ('gorilla_id', 'name', 'company', 'card_type', 'ranking')
        }),
        ('비용 조건', {
            'fields': ('annual_fee', 'annual_fee_min', 'min_spending')
        }),
        ('카테고리', {
            'fields': ('categories',)
        }),
        ('혜택 정보', {
            'fields': ('benefits_summary', 'benefits_json', 'structured_benefit'),
            'classes': ('collapse',)
        }),
        ('시간 정보', {
            'fields': ('crawled_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['sync_computed_fields', 'mark_for_reindex']

    @admin.action(description='계산 필드 동기화 (연회비, 카테고리)')
    def sync_computed_fields(self, request, queryset):
        updated = 0
        for card in queryset:
            if card.sync_computed_fields():
                card.save(update_fields=['annual_fee_min', 'categories'])
                updated += 1
        self.message_user(request, f'{updated}개 카드 업데이트됨')

    @admin.action(description='재인덱싱 대상으로 표시')
    def mark_for_reindex(self, request, queryset):
        count = 0
        for card in queryset:
            state, _ = CardEmbeddingState.objects.get_or_create(
                card=card,
                defaults={'doc_id': f'card:{card.gorilla_id}'}
            )
            if not state.needs_embedding:
                state.needs_embedding = True
                state.save(update_fields=['needs_embedding'])
                count += 1
        self.message_user(request, f'{count}개 카드가 재인덱싱 대상으로 표시됨')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'monthly_spend', 'fee_tolerance', 'min_spend_tolerance', 'updated_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(UserEvent)
class UserEventAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'card', 'event_type', 'created_at']
    list_filter = ['event_type', 'created_at']
    search_fields = ['user__username', 'card__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']


@admin.register(RecommendationLog)
class RecommendationLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'query_text_short', 'result_count', 'processing_time_ms', 'created_at']
    list_filter = ['created_at']
    search_fields = ['query_text', 'user__username']
    ordering = ['-created_at']
    readonly_fields = ['created_at']

    def query_text_short(self, obj):
        if len(obj.query_text) > 50:
            return obj.query_text[:50] + '...'
        return obj.query_text
    query_text_short.short_description = '질의'

    def result_count(self, obj):
        return len(obj.result_card_ids) if obj.result_card_ids else 0
    result_count.short_description = '결과 수'


@admin.register(CardEmbeddingState)
class CardEmbeddingStateAdmin(admin.ModelAdmin):
    list_display = ['card', 'doc_id', 'needs_embedding', 'embedding_version', 'last_indexed_at']
    list_filter = ['needs_embedding', 'embedding_version']
    search_fields = ['card__name', 'doc_id']
    ordering = ['-updated_at']
    readonly_fields = ['content_hash', 'updated_at']

    actions = ['mark_needs_embedding', 'clear_needs_embedding']

    @admin.action(description='재인덱싱 필요 표시')
    def mark_needs_embedding(self, request, queryset):
        updated = queryset.update(needs_embedding=True)
        self.message_user(request, f'{updated}개 표시됨')

    @admin.action(description='재인덱싱 필요 해제')
    def clear_needs_embedding(self, request, queryset):
        updated = queryset.update(needs_embedding=False)
        self.message_user(request, f'{updated}개 해제됨')
