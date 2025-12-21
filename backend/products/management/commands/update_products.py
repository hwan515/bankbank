from django.core.management.base import BaseCommand
from django.conf import settings
import requests
from products.models import FinancialCompany, DepositProducts, DepositOptions, SavingProducts, SavingOptions


class Command(BaseCommand):
    help = '금융감독원 API에서 금융회사 및 예적금 상품 데이터를 가져와 DB에 저장합니다.'

    def handle(self, *args, **options):
        self.stdout.write('금융 데이터 업데이트 시작...')

        # 금융회사 업데이트
        company_result = self.update_financial_companies()
        self.stdout.write(self.style.SUCCESS(f'금융회사: {company_result}'))

        # 정기예금 업데이트
        deposit_result = self.update_deposit_products()
        self.stdout.write(self.style.SUCCESS(f'정기예금: {deposit_result}'))

        # 적금 업데이트
        saving_result = self.update_saving_products()
        self.stdout.write(self.style.SUCCESS(f'적금: {saving_result}'))

        self.stdout.write(self.style.SUCCESS('금융 데이터 업데이트 완료!'))

    def update_financial_companies(self):
        API_KEY = settings.FIN_API_KEY
        url = f'http://finlife.fss.or.kr/finlifeapi/companySearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'

        try:
            response = requests.get(url)
            data = response.json()
            result = data.get('result')

            if not result:
                return {'error': 'API 응답에 result가 없습니다'}

            base_list = result.get('baseList', [])

        except Exception as e:
            return {'error': str(e)}

        created_count = 0
        updated_count = 0

        for company in base_list:
            fin_co_no = company.get('fin_co_no')
            _, created = FinancialCompany.objects.update_or_create(
                fin_co_no=fin_co_no,
                defaults={
                    'dcls_month': company.get('dcls_month') or "",
                    'kor_co_nm': company.get('kor_co_nm') or "",
                    'dcls_chrg_man': company.get('dcls_chrg_man') or "",
                    'homp_url': company.get('homp_url') or "",
                    'cal_tel': company.get('cal_tel') or "",
                }
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        return {'created': created_count, 'updated': updated_count}

    def update_deposit_products(self):
        API_KEY = settings.FIN_API_KEY
        url = f'http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'

        try:
            response = requests.get(url)
            data = response.json()
            result = data.get('result')

            if not result:
                return {'error': 'API 응답에 result가 없습니다'}

            base_list = result.get('baseList', [])
            option_list = result.get('optionList', [])

        except Exception as e:
            return {'error': str(e)}

        product_created = 0
        product_updated = 0

        for base in base_list:
            fin_prdt_cd = base.get('fin_prdt_cd')
            _, created = DepositProducts.objects.update_or_create(
                fin_prdt_cd=fin_prdt_cd,
                defaults={
                    'dcls_month': base.get('dcls_month') or "",
                    'kor_co_nm': base.get('kor_co_nm'),
                    'fin_prdt_nm': base.get('fin_prdt_nm'),
                    'etc_note': base.get('etc_note') or "",
                    'join_deny': int(base.get('join_deny')),
                    'join_member': base.get('join_member'),
                    'join_way': base.get('join_way'),
                    'spcl_cnd': base.get('spcl_cnd') or "",
                }
            )
            if created:
                product_created += 1
            else:
                product_updated += 1

        option_created = 0
        option_skipped = 0

        for option in option_list:
            fin_prdt_cd = option.get('fin_prdt_cd')
            product = DepositProducts.objects.filter(fin_prdt_cd=fin_prdt_cd).first()

            if product:
                _, created = DepositOptions.objects.get_or_create(
                    product=product,
                    fin_prdt_cd=fin_prdt_cd,
                    intr_rate_type_nm=option.get('intr_rate_type_nm'),
                    save_trm=int(option.get('save_trm')),
                    defaults={
                        'intr_rate': option.get('intr_rate'),
                        'intr_rate2': option.get('intr_rate2'),
                    }
                )
                if created:
                    option_created += 1
                else:
                    option_skipped += 1

        return {
            'products': {'created': product_created, 'updated': product_updated},
            'options': {'created': option_created, 'skipped': option_skipped}
        }

    def update_saving_products(self):
        API_KEY = settings.FIN_API_KEY
        url = f'http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'

        try:
            response = requests.get(url)
            data = response.json()
            result = data.get('result')

            if not result:
                return {'error': 'API 응답에 result가 없습니다'}

            base_list = result.get('baseList', [])
            option_list = result.get('optionList', [])

        except Exception as e:
            return {'error': str(e)}

        product_created = 0
        product_updated = 0

        for base in base_list:
            fin_prdt_cd = base.get('fin_prdt_cd')
            _, created = SavingProducts.objects.update_or_create(
                fin_prdt_cd=fin_prdt_cd,
                defaults={
                    'dcls_month': base.get('dcls_month') or "",
                    'kor_co_nm': base.get('kor_co_nm'),
                    'fin_prdt_nm': base.get('fin_prdt_nm'),
                    'etc_note': base.get('etc_note') or "",
                    'join_deny': int(base.get('join_deny')),
                    'join_member': base.get('join_member'),
                    'join_way': base.get('join_way'),
                    'spcl_cnd': base.get('spcl_cnd') or "",
                    'max_limit': base.get('max_limit'),
                }
            )
            if created:
                product_created += 1
            else:
                product_updated += 1

        option_created = 0
        option_skipped = 0

        for option in option_list:
            fin_prdt_cd = option.get('fin_prdt_cd')
            product = SavingProducts.objects.filter(fin_prdt_cd=fin_prdt_cd).first()

            if product:
                _, created = SavingOptions.objects.get_or_create(
                    product=product,
                    fin_prdt_cd=fin_prdt_cd,
                    intr_rate_type_nm=option.get('intr_rate_type_nm'),
                    save_trm=int(option.get('save_trm')),
                    rsrv_type_nm=option.get('rsrv_type_nm'),
                    defaults={
                        'intr_rate': option.get('intr_rate'),
                        'intr_rate2': option.get('intr_rate2'),
                    }
                )
                if created:
                    option_created += 1
                else:
                    option_skipped += 1

        return {
            'products': {'created': product_created, 'updated': product_updated},
            'options': {'created': option_created, 'skipped': option_skipped}
        }
