from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
import requests
from .models import (
    FinancialCompany,
    DepositProducts,
    DepositOptions,
    SavingProducts,
    SavingOptions,
    DepositSubscription,
    SavingSubscription,
)
from .serializers import (
    DepositProductsSerializer, DepositProductsListSerializer,
    SavingProductsSerializer, SavingProductsListSerializer,
    SimpleDepositProductSerializer, SimpleSavingProductSerializer,
    DepositSubscriptionSerializer, SavingSubscriptionSerializer,
)


API_KEY = settings.FIN_API_KEY

# Create your views here.
@api_view(['POST'])
@permission_classes([IsAdminUser])
def save_financial_companies(request):
    """
    금융회사 데이터 저장 (관리자 전용)
    - 권역코드: 020000(은행)
    """
    company_url = f'https://finlife.fss.or.kr/finlifeapi/companySearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'

    try:
        response = requests.get(company_url)
        response_data = response.json()

        result = response_data.get('result')
        base_list = result.get('baseList')

    except Exception as e:
        return Response({"error": f"금융감독원 API 호출 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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

    return Response({
        "message": "금융회사 데이터 저장 성공!",
        "companies": {"created": created_count, "updated": updated_count}
    }, status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def save_deposit_products(request):
    """
    정기예금 데이터 저장 (관리자 전용)
    """

    deposit_url = f'https://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'

    try:
        response = requests.get(deposit_url)
        response_data = response.json()

        # API 응답 확인
        result = response_data.get('result')
        base_list = result.get('baseList')
        option_list = result.get('optionList')
        
    except Exception as e:
        return Response({"error": f"금융감독원 API 호출 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 상품 기본 정보 저장 (BaseList)
    product_created = 0
    product_updated = 0
    for base in base_list:
        fin_prdt_cd = base.get('fin_prdt_cd')

        # 이미 있으면 수정(update), 없으면 생성(create)
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

    # 상품 옵션 정보 저장 (OptionList) - 중복 없이 신규만 저장
    option_created = 0
    option_skipped = 0
    for option in option_list:
        fin_prdt_cd = option.get('fin_prdt_cd')
        product = DepositProducts.objects.filter(fin_prdt_cd=fin_prdt_cd).first()

        if product:
            # 고유 조합으로 중복 체크: 상품 + 금리유형 + 저축기간
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

    return Response({
        "message": "정기예금 데이터 저장 성공!",
        "products": {"created": product_created, "updated": product_updated},
        "options": {"created": option_created, "skipped": option_skipped}
    }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAdminUser])
def save_saving_products(request):
    """
    적금 데이터 저장 (관리자 전용)
    """

    saving_url = f'https://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'

    try:
        response = requests.get(saving_url)
        response_data = response.json()

        # API 응답 확인
        result = response_data.get('result')
        base_list = result.get('baseList')
        option_list = result.get('optionList')

    except Exception as e:
        return Response({"error": f"금융감독원 API 호출 실패: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 적금 기본 정보 저장
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

    # 적금 옵션 정보 저장 - 중복 없이 신규만 저장
    option_created = 0
    option_skipped = 0
    for option in option_list:
        fin_prdt_cd = option.get('fin_prdt_cd')
        product = SavingProducts.objects.filter(fin_prdt_cd=fin_prdt_cd).first()

        if product:
            # 고유 조합으로 중복 체크: 상품 + 금리유형 + 저축기간 + 적립유형
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

    return Response({
        "message": "적금 데이터 저장 성공!",
        "products": {"created": product_created, "updated": product_updated},
        "options": {"created": option_created, "skipped": option_skipped}
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
def deposit_products(request):
    """
    정기예금 상품 목록 조회 (최적화)
    - 은행(금융회사)별 필터: ?bank=우리은행
    - 상품명 검색: ?search=정기예금
    - 기간 필터: ?term_months=12 (6, 12, 24, 36개월)
    - 정렬: ?ordering=intr_rate_12 (기간 미선택 시 최고 금리 기준 정렬)
    """
    from decimal import Decimal
    from django.db.models import Subquery, OuterRef, F, Value, DecimalField
    from django.db.models.functions import Coalesce, Greatest

    products = DepositProducts.objects.all()
    term_months = request.query_params.get('term_months')
    try:
        term_months = int(term_months)
    except (TypeError, ValueError):
        term_months = None
    if term_months not in [6, 12, 24, 36]:
        term_months = None

    # 기간별 최고 우대금리를 Subquery로 정의
    rate_subqueries = {}
    for term in [6, 12, 24, 36]:
        rate_subqueries[f'intr_rate_{term}'] = Subquery(
            DepositOptions.objects.filter(
                product=OuterRef('pk'),
                save_trm=term
            ).order_by('-intr_rate2')
            .values('intr_rate2')[:1]
        )

    products = products.annotate(**rate_subqueries)

    if term_months:
        products = products.filter(options__save_trm=term_months).distinct()

    # 은행(금융회사)별 필터
    bank = request.query_params.get('bank')
    if bank:
        products = products.filter(kor_co_nm__icontains=bank)

    # 상품명 검색
    search = request.query_params.get('search')
    if search:
        products = products.filter(fin_prdt_nm__icontains=search)

    # 정렬 (금리 기준)
    ordering = request.query_params.get('ordering')
    if term_months:
        products = products.order_by(F(f'intr_rate_{term_months}').desc(nulls_last=True))
    elif ordering in ['intr_rate_6', 'intr_rate_12', 'intr_rate_24', 'intr_rate_36']:
        products = products.order_by(F(ordering).desc(nulls_last=True))
    else:
        null_floor = Value(Decimal('-1.0'), output_field=DecimalField(max_digits=5, decimal_places=2))
        products = products.annotate(
            best_rate=Greatest(
                Coalesce(F('intr_rate_6'), null_floor),
                Coalesce(F('intr_rate_12'), null_floor),
                Coalesce(F('intr_rate_24'), null_floor),
                Coalesce(F('intr_rate_36'), null_floor),
                output_field=DecimalField(max_digits=5, decimal_places=2),
            )
        ).order_by('-best_rate')

    serializer = DepositProductsListSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def saving_products(request):
    """
    적금 상품 목록 조회 (최적화)
    - 은행(금융회사)별 필터: ?bank=우리은행
    - 상품명 검색: ?search=적금
    - 기간 필터: ?term_months=12 (6, 12, 24, 36개월)
    - 적립 방식: ?rsrv_type=정액/자유
    - 월 납입액: ?monthly_amount=300000 (원)
    - 정렬: ?ordering=intr_rate_12 (기간 미선택 시 최고 금리 기준 정렬)
    """
    from decimal import Decimal
    from django.db.models import Subquery, OuterRef, F, Value, Q, DecimalField
    from django.db.models.functions import Coalesce, Greatest

    products = SavingProducts.objects.all()
    term_months = request.query_params.get('term_months')
    try:
        term_months = int(term_months)
    except (TypeError, ValueError):
        term_months = None
    if term_months not in [6, 12, 24, 36]:
        term_months = None

    # 기간별 최고 우대금리를 Subquery로 정의
    rate_subqueries = {}
    for term in [6, 12, 24, 36]:
        rate_subqueries[f'intr_rate_{term}'] = Subquery(
            SavingOptions.objects.filter(
                product=OuterRef('pk'),
                save_trm=term
            ).order_by('-intr_rate2')
            .values('intr_rate2')[:1]
        )
    
    products = products.annotate(**rate_subqueries)

    if term_months:
        products = products.filter(saving_options__save_trm=term_months).distinct()

    rsrv_type = request.query_params.get('rsrv_type')
    if rsrv_type:
        if '정액' in rsrv_type:
            products = products.filter(saving_options__rsrv_type_nm__icontains='정액').distinct()
        elif '자유' in rsrv_type:
            products = products.filter(saving_options__rsrv_type_nm__icontains='자유').distinct()

    monthly_amount = request.query_params.get('monthly_amount')
    try:
        monthly_amount = int(monthly_amount)
    except (TypeError, ValueError):
        monthly_amount = None
    if monthly_amount is not None and monthly_amount > 0:
        products = products.filter(Q(max_limit__isnull=True) | Q(max_limit__gte=monthly_amount))

    # 은행(금융회사)별 필터
    bank = request.query_params.get('bank')
    if bank:
        products = products.filter(kor_co_nm__icontains=bank)

    # 상품명 검색
    search = request.query_params.get('search')
    if search:
        products = products.filter(fin_prdt_nm__icontains=search)

    # 정렬 (금리 기준)
    ordering = request.query_params.get('ordering')
    if term_months:
        products = products.order_by(F(f'intr_rate_{term_months}').desc(nulls_last=True))
    elif ordering in ['intr_rate_6', 'intr_rate_12', 'intr_rate_24', 'intr_rate_36']:
        products = products.order_by(F(ordering).desc(nulls_last=True))
    else:
        null_floor = Value(Decimal('-1.0'), output_field=DecimalField(max_digits=5, decimal_places=2))
        products = products.annotate(
            best_rate=Greatest(
                Coalesce(F('intr_rate_6'), null_floor),
                Coalesce(F('intr_rate_12'), null_floor),
                Coalesce(F('intr_rate_24'), null_floor),
                Coalesce(F('intr_rate_36'), null_floor),
                output_field=DecimalField(max_digits=5, decimal_places=2),
            )
        ).order_by('-best_rate')

    serializer = SavingProductsListSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def deposit_product_detail(request, pk):
    """
    [F03-3] 정기예금 상세 조회
    """
    product = get_object_or_404(DepositProducts, pk=pk)
    serializer = DepositProductsSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def saving_product_detail(request, pk):
    """
    [F03-3] 적금 상세 조회
    """
    product = get_object_or_404(SavingProducts, pk=pk)
    serializer = SavingProductsSerializer(product)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def bank_list(request):
    """
    은행 목록 조회 (필터용) - FinancialCompany 테이블에서 조회
    """
    companies = FinancialCompany.objects.values_list('kor_co_nm', flat=True).distinct()
    if not companies:
        # FinancialCompany가 비어있으면 상품 테이블에서 조회
        deposit_banks = DepositProducts.objects.values_list('kor_co_nm', flat=True).distinct()
        saving_banks = SavingProducts.objects.values_list('kor_co_nm', flat=True).distinct()
        banks = sorted(set(deposit_banks) | set(saving_banks))
    else:
        banks = sorted(companies)
    return Response(banks, status=status.HTTP_200_OK)


@api_view(['GET'])
def financial_companies(request):
    """
    금융회사 목록 조회
    """
    companies = FinancialCompany.objects.all().values(
        'id', 'dcls_month', 'fin_co_no', 'kor_co_nm', 'homp_url', 'cal_tel'
    )
    return Response(list(companies), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_deposit(request, pk):
    """
    [F03-3] 정기예금 가입/해제
    - term_months(6/12/24/36) 선택 후 가입
    """
    product = get_object_or_404(DepositProducts, pk=pk)
    user = request.user

    subscription = DepositSubscription.objects.filter(user=user, product=product).first()
    legacy_subscribed = product in user.deposit_products.all()

    if subscription or legacy_subscribed:
        if subscription:
            subscription.delete()
        if legacy_subscribed:
            user.deposit_products.remove(product)
        return Response({
            "message": "상품 가입이 해제되었습니다.",
            "subscribed": False
        }, status=status.HTTP_200_OK)
    else:
        term_months = request.data.get('term_months')
        try:
            term_months = int(term_months)
        except (TypeError, ValueError):
            term_months = None
        if term_months not in [6, 12, 24, 36]:
            return Response(
                {"detail": "term_months is required. (6, 12, 24, 36)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        DepositSubscription.objects.create(
            user=user,
            product=product,
            term_months=term_months,
        )
        if product not in user.deposit_products.all():
            user.deposit_products.add(product)
        return Response({
            "message": "상품에 가입되었습니다.",
            "subscribed": True,
            "term_months": term_months,
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_saving(request, pk):
    """
    [F03-3] 적금 가입/해제
    - term_months(6/12/24/36) 선택 후 가입
    """
    product = get_object_or_404(SavingProducts, pk=pk)
    user = request.user

    subscription = SavingSubscription.objects.filter(user=user, product=product).first()
    legacy_subscribed = product in user.saving_products.all()

    if subscription or legacy_subscribed:
        if subscription:
            subscription.delete()
        if legacy_subscribed:
            user.saving_products.remove(product)
        return Response({
            "message": "상품 가입이 해제되었습니다.",
            "subscribed": False
        }, status=status.HTTP_200_OK)
    else:
        term_months = request.data.get('term_months')
        try:
            term_months = int(term_months)
        except (TypeError, ValueError):
            term_months = None

        rsrv_type = (request.data.get('rsrv_type') or '').strip()
        monthly_amount = request.data.get('monthly_amount')
        try:
            monthly_amount = int(monthly_amount)
        except (TypeError, ValueError):
            monthly_amount = None
        if monthly_amount is not None and monthly_amount <= 0:
            monthly_amount = None

        if term_months not in [6, 12, 24, 36]:
            return Response(
                {"detail": "term_months is required. (6, 12, 24, 36)"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        SavingSubscription.objects.create(
            user=user,
            product=product,
            term_months=term_months,
            rsrv_type=rsrv_type,
            monthly_amount=monthly_amount,
        )
        if product not in user.saving_products.all():
            user.saving_products.add(product)
        return Response({
            "message": "상품에 가입되었습니다.",
            "subscribed": True,
            "term_months": term_months,
            "rsrv_type": rsrv_type,
            "monthly_amount": monthly_amount,
        }, status=status.HTTP_201_CREATED)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_subscription(request, product_type, pk):
    """
    [F03-3] 상품 가입 여부 확인
    - product_type: 'deposit' 또는 'saving'
    """
    user = request.user

    if product_type == 'deposit':
        product = get_object_or_404(DepositProducts, pk=pk)
        subscription = DepositSubscription.objects.filter(user=user, product=product).first()
        if subscription:
            return Response({
                "subscribed": True,
                "term_months": subscription.term_months,
            }, status=status.HTTP_200_OK)
        subscribed = product in user.deposit_products.all()
        if subscribed:
            return Response({
                "subscribed": True,
                "term_months": None,
            }, status=status.HTTP_200_OK)
    elif product_type == 'saving':
        product = get_object_or_404(SavingProducts, pk=pk)
        subscription = SavingSubscription.objects.filter(user=user, product=product).first()
        if subscription:
            return Response({
                "subscribed": True,
                "term_months": subscription.term_months,
                "rsrv_type": subscription.rsrv_type,
                "monthly_amount": subscription.monthly_amount,
            }, status=status.HTTP_200_OK)
        subscribed = product in user.saving_products.all()
        if subscribed:
            return Response({
                "subscribed": True,
                "term_months": None,
                "rsrv_type": "",
                "monthly_amount": None,
            }, status=status.HTTP_200_OK)
    else:
        return Response({"error": "Invalid product type"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"subscribed": subscribed}, status=status.HTTP_200_OK)


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_subscription(request, product_type, pk):
    """
    [F03-3] 구독 기간 변경
    - term_months 필수
    """
    user = request.user
    term_months = request.data.get('term_months')
    try:
        term_months = int(term_months)
    except (TypeError, ValueError):
        term_months = None
    if term_months not in [6, 12, 24, 36]:
        return Response(
            {"detail": "term_months is required. (6, 12, 24, 36)"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    if product_type == 'deposit':
        product = get_object_or_404(DepositProducts, pk=pk)
        if not DepositOptions.objects.filter(product=product, save_trm=term_months).exists():
            return Response(
                {"detail": "해당 기간의 예금 옵션이 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = DepositSubscription.objects.filter(user=user, product=product).first()
        if not subscription:
            if product not in user.deposit_products.all():
                return Response({"detail": "구독 정보가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
            subscription = DepositSubscription.objects.create(
                user=user,
                product=product,
                term_months=term_months,
            )
        else:
            subscription.term_months = term_months
            subscription.save(update_fields=['term_months', 'updated_at'])

        if product not in user.deposit_products.all():
            user.deposit_products.add(product)

        return Response({
            "subscribed": True,
            "term_months": subscription.term_months,
        }, status=status.HTTP_200_OK)

    if product_type == 'saving':
        product = get_object_or_404(SavingProducts, pk=pk)
        rsrv_type = (request.data.get('rsrv_type') or '').strip()
        monthly_amount = request.data.get('monthly_amount')
        monthly_amount_set = 'monthly_amount' in request.data
        try:
            monthly_amount = int(monthly_amount)
        except (TypeError, ValueError):
            monthly_amount = None
        if monthly_amount is not None and monthly_amount <= 0:
            monthly_amount = None

        rsrv_filter = ''
        if rsrv_type:
            if '정액' in rsrv_type:
                rsrv_filter = '정액'
            elif '자유' in rsrv_type:
                rsrv_filter = '자유'
            else:
                rsrv_filter = rsrv_type

        option_qs = SavingOptions.objects.filter(product=product, save_trm=term_months)
        if rsrv_filter:
            option_qs = option_qs.filter(rsrv_type_nm__icontains=rsrv_filter)
        if not option_qs.exists():
            return Response(
                {"detail": "해당 기간의 적금 옵션이 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        subscription = SavingSubscription.objects.filter(user=user, product=product).first()
        if not subscription:
            if product not in user.saving_products.all():
                return Response({"detail": "구독 정보가 없습니다."}, status=status.HTTP_404_NOT_FOUND)
            subscription = SavingSubscription.objects.create(
                user=user,
                product=product,
                term_months=term_months,
                rsrv_type=rsrv_type,
                monthly_amount=monthly_amount,
            )
        else:
            subscription.term_months = term_months
            if rsrv_type:
                subscription.rsrv_type = rsrv_type
            if monthly_amount_set:
                subscription.monthly_amount = monthly_amount
            subscription.save(update_fields=['term_months', 'rsrv_type', 'monthly_amount', 'updated_at'])

        if product not in user.saving_products.all():
            user.saving_products.add(product)

        return Response({
            "subscribed": True,
            "term_months": subscription.term_months,
            "rsrv_type": subscription.rsrv_type,
            "monthly_amount": subscription.monthly_amount,
        }, status=status.HTTP_200_OK)

    return Response({"error": "Invalid product type"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_subscriptions(request):
    """
    사용자가 가입한 예금/적금 목록 조회
    """
    user = request.user
    deposit_subs = DepositSubscription.objects.filter(user=user).select_related('product')
    saving_subs = SavingSubscription.objects.filter(user=user).select_related('product')

    deposits = DepositSubscriptionSerializer(deposit_subs, many=True).data
    savings = SavingSubscriptionSerializer(saving_subs, many=True).data

    deposit_ids = {sub.product_id for sub in deposit_subs}
    saving_ids = {sub.product_id for sub in saving_subs}

    fallback_deposits = user.deposit_products.exclude(id__in=deposit_ids)
    fallback_savings = user.saving_products.exclude(id__in=saving_ids)

    if fallback_deposits.exists():
        for item in SimpleDepositProductSerializer(fallback_deposits, many=True).data:
            deposits.append({**item, "term_months": None})
    if fallback_savings.exists():
        for item in SimpleSavingProductSerializer(fallback_savings, many=True).data:
            savings.append({**item, "term_months": None, "rsrv_type": "", "monthly_amount": None})

    return Response({
        "deposits": deposits,
        "savings": savings,
    }, status=status.HTTP_200_OK)
