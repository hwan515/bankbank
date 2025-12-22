from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
import requests
from .models import FinancialCompany, DepositProducts, DepositOptions, SavingProducts, SavingOptions
from .serializers import (
    DepositProductsSerializer, DepositProductsListSerializer,
    SavingProductsSerializer, SavingProductsListSerializer
)


API_KEY = settings.FIN_API_KEY

# Create your views here.
@api_view(['GET'])
def save_financial_companies(request):
    """
    금융회사 데이터 저장
    - 권역코드: 020000(은행)
    """
    company_url = f'http://finlife.fss.or.kr/finlifeapi/companySearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'

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

@api_view(['GET'])
def save_deposit_products(request):
    """
    정기예금 데이터 저장
    """

    deposit_url = f'http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'

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


@api_view(['GET'])
def save_saving_products(request):
    """
    적금 데이터 저장
    """
    
    saving_url = f'http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'

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
    정기예금 상품 목록 조회
    - 은행(금융회사)별 필터: ?bank=우리은행
    - 상품명 검색: ?search=정기예금
    - 정렬: ?ordering=intr_rate_12 (6, 12, 24, 36개월 금리 기준)
    """
    products = DepositProducts.objects.prefetch_related('options').all()

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
    if ordering in ['intr_rate_6', 'intr_rate_12', 'intr_rate_24', 'intr_rate_36']:
        term = int(ordering.split('_')[-1])
        # 해당 기간 옵션이 있는 상품만 필터링 후 금리 순 정렬
        products = products.filter(options__save_trm=term).distinct()
        products = sorted(
            products,
            key=lambda p: p.options.filter(save_trm=term).first().intr_rate2 or 0 if p.options.filter(save_trm=term).exists() else 0,
            reverse=True
        )

    serializer = DepositProductsListSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def saving_products(request):
    """
    적금 상품 목록 조회
    - 은행(금융회사)별 필터: ?bank=우리은행
    - 상품명 검색: ?search=적금
    - 정렬: ?ordering=intr_rate_12 (6, 12, 24, 36개월 금리 기준)
    """
    products = SavingProducts.objects.prefetch_related('saving_options').all()

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
    if ordering in ['intr_rate_6', 'intr_rate_12', 'intr_rate_24', 'intr_rate_36']:
        term = int(ordering.split('_')[-1])
        products = products.filter(saving_options__save_trm=term).distinct()
        products = sorted(
            products,
            key=lambda p: p.saving_options.filter(save_trm=term).first().intr_rate2 or 0 if p.saving_options.filter(save_trm=term).exists() else 0,
            reverse=True
        )

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
    - 이미 가입된 상품이면 해제, 아니면 가입
    """
    product = get_object_or_404(DepositProducts, pk=pk)
    user = request.user

    if product in user.deposit_products.all():
        user.deposit_products.remove(product)
        return Response({
            "message": "상품 가입이 해제되었습니다.",
            "subscribed": False
        }, status=status.HTTP_200_OK)
    else:
        user.deposit_products.add(product)
        return Response({
            "message": "상품에 가입되었습니다.",
            "subscribed": True
        }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def subscribe_saving(request, pk):
    """
    [F03-3] 적금 가입/해제
    - 이미 가입된 상품이면 해제, 아니면 가입
    """
    product = get_object_or_404(SavingProducts, pk=pk)
    user = request.user

    if product in user.saving_products.all():
        user.saving_products.remove(product)
        return Response({
            "message": "상품 가입이 해제되었습니다.",
            "subscribed": False
        }, status=status.HTTP_200_OK)
    else:
        user.saving_products.add(product)
        return Response({
            "message": "상품에 가입되었습니다.",
            "subscribed": True
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
        subscribed = product in user.deposit_products.all()
    elif product_type == 'saving':
        product = get_object_or_404(SavingProducts, pk=pk)
        subscribed = product in user.saving_products.all()
    else:
        return Response({"error": "Invalid product type"}, status=status.HTTP_400_BAD_REQUEST)

    return Response({"subscribed": subscribed}, status=status.HTTP_200_OK)