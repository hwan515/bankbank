import json
import sqlite3
from datetime import datetime
from django.core.management.base import BaseCommand
from cards.models import Card


class Command(BaseCommand):
    help = 'capstone_project의 SQLite cards_card 테이블을 MySQL로 마이그레이션'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source-db',
            default='../../capstone_project/backend/db.sqlite3',
            help='SQLite DB 경로 (기본: ../../capstone_project/backend/db.sqlite3)'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='마이그레이션할 카드 수 제한 (0=전체)'
        )
        parser.add_argument(
            '--update',
            action='store_true',
            help='기존 데이터 업데이트 (기본: 새 데이터만 추가)'
        )

    def handle(self, *args, **options):
        source_db = options['source_db']
        limit = options['limit']
        update_mode = options['update']

        self.stdout.write(f'SQLite DB 연결: {source_db}')

        try:
            conn = sqlite3.connect(source_db)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            # 카드 데이터 조회
            query = 'SELECT * FROM cards_card ORDER BY ranking ASC NULLS LAST, id ASC'
            if limit > 0:
                query += f' LIMIT {limit}'

            cursor.execute(query)
            rows = cursor.fetchall()

            self.stdout.write(f'총 {len(rows)}개 카드 발견')

            created_count = 0
            updated_count = 0
            skipped_count = 0

            for row in rows:
                gorilla_id = row['gorilla_id']

                # JSON 필드 파싱
                benefits_json = []
                structured_benefit = []

                try:
                    if row['benefits_json']:
                        benefits_json = json.loads(row['benefits_json'])
                except (json.JSONDecodeError, TypeError):
                    pass

                try:
                    if row['structured_benefit']:
                        structured_benefit = json.loads(row['structured_benefit'])
                except (json.JSONDecodeError, TypeError):
                    pass

                # crawled_at 파싱
                crawled_at = None
                if row['crawled_at']:
                    try:
                        crawled_at = datetime.fromisoformat(row['crawled_at'].replace('Z', '+00:00'))
                    except (ValueError, AttributeError):
                        pass

                card_data = {
                    'name': row['name'],
                    'company': row['company'],
                    'card_type': row['card_type'],
                    'annual_fee': row['annual_fee'] or '',
                    'min_spending': row['min_spending'] or 0,
                    'benefits_summary': row['benefits_summary'] or '',
                    'benefits_json': benefits_json,
                    'structured_benefit': structured_benefit,
                    'ranking': row['ranking'],
                    'crawled_at': crawled_at,
                }

                try:
                    card, created = Card.objects.get_or_create(
                        gorilla_id=gorilla_id,
                        defaults=card_data
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(f'  + {card.company} - {card.name}')
                    elif update_mode:
                        for key, value in card_data.items():
                            setattr(card, key, value)
                        card.save()
                        updated_count += 1
                        self.stdout.write(f'  ~ {card.company} - {card.name}')
                    else:
                        skipped_count += 1

                except Exception as e:
                    self.stderr.write(f'  ! 오류 (gorilla_id={gorilla_id}): {e}')

            conn.close()

            self.stdout.write(self.style.SUCCESS(
                f'\n완료: 생성 {created_count}개, 업데이트 {updated_count}개, 스킵 {skipped_count}개'
            ))

        except sqlite3.Error as e:
            self.stderr.write(self.style.ERROR(f'SQLite 오류: {e}'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'오류: {e}'))
