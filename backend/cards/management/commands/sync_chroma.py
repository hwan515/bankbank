import os
from datetime import datetime
from django.core.management.base import BaseCommand
from django.utils import timezone
from cards.models import Card, CardEmbeddingState


class Command(BaseCommand):
    help = 'Card 데이터를 Chroma 벡터 DB에 동기화 (임베딩 생성 및 업서트)'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='모든 카드 재인덱싱 (기본: 변경된 카드만)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='처리할 카드 수 제한 (0=전체)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=50,
            help='배치 크기 (기본: 50)'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='실제 임베딩/업서트 없이 대상만 확인'
        )
        parser.add_argument(
            '--sync-computed',
            action='store_true',
            help='Card의 계산 필드(annual_fee_min, categories 등)도 동기화'
        )
        parser.add_argument(
            '--ranking-min',
            type=int,
            default=0,
            help='최소 ranking (0=제한 없음)'
        )
        parser.add_argument(
            '--ranking-max',
            type=int,
            default=0,
            help='최대 ranking (0=제한 없음)'
        )

    def handle(self, *args, **options):
        reindex_all = options['all']
        limit = options['limit']
        batch_size = options['batch_size']
        dry_run = options['dry_run']
        sync_computed = options['sync_computed']
        self.ranking_min = options['ranking_min']
        self.ranking_max = options['ranking_max']

        # 1. 계산 필드 동기화 (옵션)
        if sync_computed:
            self.sync_computed_fields()

        # 2. 임베딩 대상 카드 수집
        cards_to_index = self.get_cards_to_index(reindex_all, limit)

        if not cards_to_index:
            self.stdout.write(self.style.SUCCESS('동기화할 카드가 없습니다.'))
            return

        self.stdout.write(f'동기화 대상: {len(cards_to_index)}개 카드')

        if dry_run:
            for card in cards_to_index[:20]:
                self.stdout.write(f'  - {card.company} / {card.name}')
            if len(cards_to_index) > 20:
                self.stdout.write(f'  ... 외 {len(cards_to_index) - 20}개')
            self.stdout.write(self.style.WARNING('Dry-run 모드: 실제 인덱싱 생략'))
            return

        # 3. Chroma 클라이언트 초기화
        try:
            chroma_client, collection, embeddings = self.get_chroma_client()
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Chroma 연결 실패: {e}'))
            return

        # 4. 배치 처리
        success_count = 0
        error_count = 0

        for i in range(0, len(cards_to_index), batch_size):
            batch = cards_to_index[i:i + batch_size]
            self.stdout.write(f'\n배치 {i // batch_size + 1}: {len(batch)}개 처리 중...')

            try:
                success, errors = self.index_batch(batch, collection, embeddings)
                success_count += success
                error_count += errors
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'배치 처리 오류: {e}'))
                error_count += len(batch)

        self.stdout.write(self.style.SUCCESS(
            f'\n완료: 성공 {success_count}개, 실패 {error_count}개'
        ))

    def sync_computed_fields(self):
        """Card의 계산 필드 동기화"""
        self.stdout.write('계산 필드 동기화 중...')

        updated = 0
        for card in Card.objects.all():
            if card.sync_computed_fields():
                card.save(update_fields=['annual_fee_min', 'categories'])
                updated += 1

        self.stdout.write(f'  계산 필드 업데이트: {updated}개')

    def get_cards_to_index(self, reindex_all: bool, limit: int):
        """인덱싱 대상 카드 목록 반환"""
        if reindex_all:
            qs = Card.objects.all().order_by('ranking', '-created_at')
        else:
            # CardEmbeddingState가 없거나 needs_embedding=True인 카드
            cards_with_state = CardEmbeddingState.objects.filter(
                needs_embedding=True
            ).values_list('card_id', flat=True)

            cards_without_state = Card.objects.exclude(
                id__in=CardEmbeddingState.objects.values_list('card_id', flat=True)
            ).values_list('id', flat=True)

            target_ids = set(cards_with_state) | set(cards_without_state)
            qs = Card.objects.filter(id__in=target_ids).order_by('ranking', '-created_at')

        # ranking 필터 적용
        if self.ranking_min > 0:
            qs = qs.filter(ranking__gte=self.ranking_min)
        if self.ranking_max > 0:
            qs = qs.filter(ranking__lte=self.ranking_max)

        if limit > 0:
            qs = qs[:limit]

        return list(qs)

    def get_chroma_client(self):
        """Chroma 클라이언트 및 컬렉션 반환"""
        import chromadb
        from langchain_openai import OpenAIEmbeddings
        from django.conf import settings
        from dotenv import load_dotenv
        from pathlib import Path

        # .env 파일 로드
        project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        load_dotenv(project_root / 'backend' / '.env')
        load_dotenv(project_root / 'analyze_card' / '.env')

        # GMS API 키 (OpenAI 호환)
        gms_api_key = os.getenv('GMS_KEY', '')
        if not gms_api_key:
            raise ValueError("GMS_KEY 환경 변수가 설정되지 않았습니다.")

        chroma_host = getattr(settings, 'CHROMA_HOST', None) or os.getenv('CHROMA_HOST', 'chroma.cocohwan.site')
        chroma_port = int(getattr(settings, 'CHROMA_PORT', None) or os.getenv('CHROMA_PORT', '443'))
        collection_name = getattr(settings, 'CHROMA_COLLECTION', None) or os.getenv('CHROMA_COLLECTION', 'cards_top100_text')
        model_name = os.getenv('EMBED_MODEL', 'text-embedding-3-large')

        self.stdout.write(f'Chroma 연결: {chroma_host}:{chroma_port} / {collection_name}')
        self.stdout.write(f'임베딩 모델: {model_name} (GMS API)')

        client = chromadb.HttpClient(
            host=chroma_host,
            port=chroma_port,
            ssl=True,
        )

        # 컬렉션 가져오기 또는 생성
        collection = client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )

        # GMS API를 통한 OpenAI 임베딩 (text-embedding-3-large)
        embeddings = OpenAIEmbeddings(
            api_key=gms_api_key,
            base_url="https://gms.ssafy.io/gmsapi/api.openai.com/v1",
            model=model_name,
        )

        return client, collection, embeddings

    def index_batch(self, cards, collection, embeddings):
        """배치 카드 인덱싱"""
        success = 0
        errors = 0

        ids = []
        documents = []
        metadatas = []

        for card in cards:
            try:
                doc_id = f"card:{card.gorilla_id}"
                text = card.build_embedding_text()

                ids.append(doc_id)
                documents.append(text)
                metadatas.append({
                    'gorilla_id': card.gorilla_id,
                    'name': card.name,
                    'company': card.company,
                    'card_type': card.card_type,
                    'ranking': card.ranking or 999999,
                    'min_spending': card.min_spending,
                    'annual_fee_min': card.annual_fee_min,
                    'primary_category': card.primary_category,  # 첫 번째 카테고리 (호환성)
                    'categories': ','.join(card.categories) if card.categories else '',  # 모든 카테고리
                })
            except Exception as e:
                self.stderr.write(f'  ! 텍스트 생성 오류 ({card.gorilla_id}): {e}')
                errors += 1

        if not documents:
            return success, errors

        try:
            # 임베딩 생성
            self.stdout.write(f'  임베딩 생성 중 ({len(documents)}개)...')
            embeddings_list = embeddings.embed_documents(documents)

            # Chroma 업서트
            self.stdout.write(f'  Chroma 업서트 중...')
            collection.upsert(
                ids=ids,
                embeddings=embeddings_list,
                documents=documents,
                metadatas=metadatas,
            )

            # CardEmbeddingState 업데이트
            now = timezone.now()
            for card, doc_id, text in zip(cards, ids, documents):
                state, _ = CardEmbeddingState.objects.get_or_create(
                    card=card,
                    defaults={'doc_id': doc_id}
                )
                state.doc_id = doc_id
                state.content_hash = CardEmbeddingState.make_hash(text)
                state.needs_embedding = False
                state.last_indexed_at = now
                state.save()

                success += 1
                self.stdout.write(f'  + {card.company} / {card.name}')

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'  ! 배치 업서트 오류: {e}'))
            errors += len(documents)

        return success, errors
