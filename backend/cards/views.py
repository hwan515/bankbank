from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db.models import Q

from .models import Card
from .serializers import CardListSerializer, CardDetailSerializer, CardRecommendRequestSerializer


@api_view(['GET'])
@permission_classes([AllowAny])
def card_list(request):
    """
    GET /cards/ - 카드 목록 조회 (검색, 필터링, 페이지네이션)
    query params:
      - q: 검색어 (카드명, 회사명)
      - company: 카드사 필터
      - card_type: credit/check
      - page: 페이지 번호 (기본 1)
      - page_size: 페이지 크기 (기본 20, 최대 100)
    """
    queryset = Card.objects.all()

    # 검색어 필터
    q = request.query_params.get('q', '').strip()
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) | Q(company__icontains=q) | Q(benefits_summary__icontains=q)
        )

    # 카드사 필터
    company = request.query_params.get('company', '').strip()
    if company:
        queryset = queryset.filter(company=company)

    # 카드 타입 필터
    card_type = request.query_params.get('card_type', '').strip()
    if card_type in ['credit', 'check']:
        queryset = queryset.filter(card_type=card_type)

    # 정렬: 랭킹 우선, 없으면 최신순
    queryset = queryset.order_by('ranking', '-created_at')

    # 페이지네이션
    page = int(request.query_params.get('page', 1))
    page_size = min(int(request.query_params.get('page_size', 20)), 100)
    start = (page - 1) * page_size
    end = start + page_size

    total_count = queryset.count()
    cards = queryset[start:end]

    serializer = CardListSerializer(cards, many=True, context={'request': request})

    return Response({
        'results': serializer.data,
        'count': total_count,
        'page': page,
        'page_size': page_size,
        'total_pages': (total_count + page_size - 1) // page_size
    })


@api_view(['GET'])
@permission_classes([AllowAny])
def card_detail(request, pk):
    """
    GET /cards/<id>/ - 카드 상세 조회
    """
    try:
        card = Card.objects.get(pk=pk)
    except Card.DoesNotExist:
        return Response(
            {'detail': '카드를 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = CardDetailSerializer(card, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def card_companies(request):
    """
    GET /cards/companies/ - 카드사 목록 조회
    """
    companies = Card.objects.values_list('company', flat=True).distinct().order_by('company')
    return Response(list(companies))


@api_view(['POST'])
@permission_classes([AllowAny])
def card_recommend(request):
    """
    POST /cards/card-recommendation/ - AI 기반 카드 추천
    body: { "query": "스타벅스 할인 많은 카드", "k": 5 }
    """
    serializer = CardRecommendRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    query = serializer.validated_data['query']
    k = serializer.validated_data.get('k', 5)

    try:
        from .services.recommend import CardRecommendService
        service = CardRecommendService()
        results = service.recommend(query, k=k)

        # 결과를 Card 모델과 매핑
        response_data = []
        for hit in results:
            try:
                card = Card.objects.get(gorilla_id=hit.gorilla_id)
                response_data.append({
                    'card': CardListSerializer(card, context={'request': request}).data,
                    'score': hit.score,
                    'preview': hit.preview,
                })
            except Card.DoesNotExist:
                # DB에 해당 카드가 없으면 Chroma 메타데이터로 간이 응답
                response_data.append({
                    'card': {
                        'gorilla_id': hit.gorilla_id,
                        'name': hit.name,
                        'company': hit.company,
                        'ranking': hit.ranking,
                        'image_url': f'https://cardimage.cocohwan.site/{hit.gorilla_id}.png',
                    },
                    'score': hit.score,
                    'preview': hit.preview,
                })

        return Response(response_data)

    except Exception as e:
        return Response(
            {'detail': f'추천 서비스 오류: {str(e)}'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )
