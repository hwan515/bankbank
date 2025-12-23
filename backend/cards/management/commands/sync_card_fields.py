from django.core.management.base import BaseCommand
from cards.models import Card, CardEmbeddingState


class Command(BaseCommand):
    help = 'Card 모델의 계산 필드(annual_fee_min, categories 등) 동기화'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mark-reindex',
            action='store_true',
            help='변경된 카드의 needs_embedding 플래그 설정'
        )

    def handle(self, *args, **options):
        mark_reindex = options['mark_reindex']

        self.stdout.write('Card 계산 필드 동기화 시작...')

        updated = 0
        unchanged = 0

        for card in Card.objects.all():
            if card.sync_computed_fields():
                card.save(update_fields=['annual_fee_min', 'categories'])
                updated += 1
                self.stdout.write(f'  ~ {card.company} / {card.name}')

                if mark_reindex:
                    state, _ = CardEmbeddingState.objects.get_or_create(
                        card=card,
                        defaults={'doc_id': f'card:{card.gorilla_id}'}
                    )
                    if not state.needs_embedding:
                        state.needs_embedding = True
                        state.save(update_fields=['needs_embedding'])
            else:
                unchanged += 1

        self.stdout.write(self.style.SUCCESS(
            f'\n완료: 업데이트 {updated}개, 변경없음 {unchanged}개'
        ))

        if mark_reindex and updated > 0:
            self.stdout.write(f'{updated}개 카드가 재인덱싱 대상으로 표시됨')
            self.stdout.write('python manage.py sync_chroma 명령으로 Chroma 동기화 필요')
