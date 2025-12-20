from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
import requests
from .models import DepositProducts, DepositOptions, SavingProducts, SavingOptions
from .serializers import DepositProductsSerializer, SavingProductsSerializer


API_KEY = settings.FIN_API_KEY

# Create your views here.
@api_view(['GET'])
def save_deposit_products(request):
    """
    [F03-1] 정기예금 데이터 저장
    """

    deposit_url = f'http://finlife.fss.or.kr/finlifeapi/depositProductsSearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'

    try:
        response = requests.get(deposit_url)
        response_data = response.json()

        # API 응답 확인
        result = response_data.get('result')
        if result is None:
            return Response({"error": "API 응답에 result가 없습니다", "response": response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        base_list = result.get('baseList')
        option_list = result.get('optionList')

        if base_list is None:
            return Response({"error": "API 응답에 baseList가 없습니다", "response": response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    [F03-1] 적금 데이터 저장 (적금 전용 로직 포함)
    """
    
    saving_url = f'http://finlife.fss.or.kr/finlifeapi/savingProductsSearch.json?auth={API_KEY}&topFinGrpNo=020000&pageNo=1'

    try:
        response = requests.get(saving_url)
        response_data = response.json()

        # API 응답 확인
        result = response_data.get('result')
        if result is None:
            return Response({"error": "API 응답에 result가 없습니다", "response": response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        base_list = result.get('baseList')
        option_list = result.get('optionList')

        if base_list is None:
            return Response({"error": "API 응답에 baseList가 없습니다", "response": response_data}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    [F03-2] 정기예금 상품 목록 조회
    """
    products = DepositProducts.objects.all()
    serializer = DepositProductsSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
def saving_products(request):
    """
    [F03-2] 적금 상품 목록 조회
    """
    products = SavingProducts.objects.all()
    serializer = SavingProductsSerializer(products, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)