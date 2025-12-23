import time
import re
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q

from .models import Card, UserProfile, UserEvent, RecommendationLog
from .serializers import (
    CardListSerializer, CardDetailSerializer,
    CardRecommendRequestSerializer,
    UserProfileSerializer, UserEventCreateSerializer
)


@api_view(['GET'])
@permission_classes([AllowAny])
def card_list(request):
    """
    GET /cards/ - 카드 목록 조회 (검색, 필터링, 페이지네이션)
    query params:
      - q: 검색어 (카드명, 회사명, 혜택)
      - company: 카드사 필터
      - card_type: CRD/CHK
      - category: 카테고리 코드 (COFFEE, FOOD 등)
      - max_annual_fee: 연회비 상한
      - max_min_spending: 전월실적 상한
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
    if card_type in ['CRD', 'CHK']:
        queryset = queryset.filter(card_type=card_type)

    # 카테고리 필터 (다중 카테고리 지원)
    category = request.query_params.get('category', '').strip()
    if category:
        # categories JSONField에서 해당 카테고리 포함 여부 확인
        queryset = queryset.filter(categories__contains=[category])

    # 연회비 상한 필터
    max_annual_fee = request.query_params.get('max_annual_fee')
    if max_annual_fee:
        try:
            queryset = queryset.filter(annual_fee_min__lte=int(max_annual_fee))
        except ValueError:
            pass

    # 전월실적 상한 필터
    max_min_spending = request.query_params.get('max_min_spending')
    if max_min_spending:
        try:
            queryset = queryset.filter(min_spending__lte=int(max_min_spending))
        except ValueError:
            pass

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


@api_view(['GET'])
@permission_classes([AllowAny])
def card_categories(request):
    """
    GET /cards/categories/ - 카테고리 목록 조회
    """
    return Response(dict(Card.CATEGORY_CHOICES))


@api_view(['POST'])
@permission_classes([AllowAny])
def card_recommend(request):
    """
    POST /cards/card-recommendation/ - AI 기반 카드 추천

    body: {
        "query": "스타벅스 할인 많은 카드",
        "k": 5,
        "company": "",
        "card_type": "CRD",
        "max_annual_fee": 20000,
        "max_min_spending": 300000,
        "category_weights": {"COFFEE": 3, "FOOD": 2}
    }
    """
    serializer = CardRecommendRequestSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    query = serializer.validated_data['query']
    k = serializer.validated_data.get('k', 5)

    # 필터 구성
    filters = {
        'company': serializer.validated_data.get('company'),
        'card_type': serializer.validated_data.get('card_type'),
        'max_annual_fee': serializer.validated_data.get('max_annual_fee'),
        'max_min_spending': serializer.validated_data.get('max_min_spending'),
        'category_weights': serializer.validated_data.get('category_weights', {}),
    }

    # --- Query에서 하드 필터 추출 ---
    # 1. 카드사
    if not filters.get('company'):
        all_companies = Card.objects.values_list('company', flat=True).distinct()
        for comp in all_companies:
            if comp in query:
                filters['company'] = comp
                break
    
    # 2. 카드 종류
    if not filters.get('card_type'):
        if '체크카드' in query or '체크 카드' in query:
            filters['card_type'] = 'CHK'
        elif '신용카드' in query or '신용 카드' in query:
            filters['card_type'] = 'CRD'

    # 3. 연회비
    if filters.get('max_annual_fee') is None:
        if '연회비 없는' in query or '연회비 무료' in query:
            filters['max_annual_fee'] = 0
        else:
            # "연회비 1만원", "연회비 2만" 등 패턴
            match = re.search(r'연회비\s*(\d+)\s*만', query)
            if match:
                try:
                    filters['max_annual_fee'] = int(match.group(1)) * 10000
                except (ValueError, IndexError):
                    pass

    # 4. 전월실적
    if filters.get('max_min_spending') is None:
        if '실적 없는' in query or '무실적' in query or '실적무관' in query:
            filters['max_min_spending'] = 0
        else:
            # "실적 30만원", "전월실적 50만" 등 패턴
            match = re.search(r'(?:전월실적|실적)\s*(\d+)\s*만', query)
            if match:
                try:
                    filters['max_min_spending'] = int(match.group(1)) * 10000
                except (ValueError, IndexError):
                    pass
    # --- 필터 추출 끝 ---

    # --- 로그인 사용자의 UserProfile 자동 적용 ---
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(user=request.user)
            # 카테고리 가중치가 설정되어 있고, 요청에서 지정하지 않은 경우 자동 적용
            if profile.category_weights and not filters.get('category_weights'):
                filters['category_weights'] = profile.category_weights
            # 연회비 허용치 자동 적용
            if profile.fee_tolerance and filters.get('max_annual_fee') is None:
                filters['max_annual_fee'] = profile.fee_tolerance
            # 전월실적 허용치 자동 적용
            if profile.min_spend_tolerance and filters.get('max_min_spending') is None:
                filters['max_min_spending'] = profile.min_spend_tolerance
        except UserProfile.DoesNotExist:
            pass
    # --- UserProfile 적용 끝 ---

    start_time = time.time()

    try:
        from .services.recommend import CardRecommendService
        service = CardRecommendService()
        hits = service.recommend(query, k=k, filters=filters)

        processing_time_ms = int((time.time() - start_time) * 1000)

        # bulk 조회 (N+1 제거)
        gids = [h.gorilla_id for h in hits]
        cards = Card.objects.filter(gorilla_id__in=gids)
        card_map = {c.gorilla_id: c for c in cards}

        response_data = []
        result_card_ids = []
        result_scores = []

        for h in hits:
            card = card_map.get(h.gorilla_id)
            if card:
                response_data.append({
                    'card': CardListSerializer(card, context={'request': request}).data,
                    'score': round(h.score, 4),
                    'semantic_score': round(h.semantic_score, 4),
                    'fit_score': round(h.fit_score, 4),
                    'reasons': h.reasons,
                    'preview': h.preview,
                })
                result_card_ids.append(card.id)
                result_scores.append(round(h.score, 4))
            else:
                # DB에 없으면 metadata 기반 fallback
                response_data.append({
                    'card': {
                        'gorilla_id': h.gorilla_id,
                        'name': h.name,
                        'company': h.company,
                        'ranking': h.ranking,
                        'image_url': f'https://cardimage.cocohwan.site/{h.gorilla_id}.png',
                    },
                    'score': round(h.score, 4),
                    'semantic_score': round(h.semantic_score, 4),
                    'fit_score': round(h.fit_score, 4),
                    'reasons': h.reasons,
                    'preview': h.preview,
                })

        # 추천 로그 저장
        try:
            RecommendationLog.objects.create(
                user=request.user if request.user.is_authenticated else None,
                session_id=request.session.session_key or '',
                query_text=query,
                filters=filters,
                result_card_ids=result_card_ids,
                result_scores=result_scores,
                processing_time_ms=processing_time_ms,
            )
        except Exception:
            pass  # 로그 저장 실패해도 추천 결과는 반환

        return Response({
            'results': response_data,
            'query': query,
            'filters': filters,
            'processing_time_ms': processing_time_ms,
        })

    except Exception as e:
        return Response(
            {'detail': f'추천 서비스 오류: {str(e)}'},
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def card_event(request):
    """
    POST /cards/events/ - 사용자 행동 로그 저장
    body: { "card_id": 1, "event_type": "CLICK", "context": {} }
    """
    serializer = UserEventCreateSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    card_id = serializer.validated_data['card_id']
    event_type = serializer.validated_data['event_type']
    context = serializer.validated_data.get('context', {})

    try:
        card = Card.objects.get(pk=card_id)
    except Card.DoesNotExist:
        return Response(
            {'detail': '카드를 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

    UserEvent.objects.create(
        user=request.user if request.user.is_authenticated else None,
        card=card,
        event_type=event_type,
        context=context,
        session_id=request.session.session_key or '',
    )

    return Response({'status': 'ok'}, status=status.HTTP_201_CREATED)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    """
    GET/PUT /cards/profile/ - 사용자 추천 프로필 조회/수정
    """
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'GET':
        serializer = UserProfileSerializer(profile)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UserProfileSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_like(request, pk):
    """
    POST /cards/<id>/like/ - 카드 좋아요 토글
    """
    try:
        card = Card.objects.get(pk=pk)
    except Card.DoesNotExist:
        return Response(
            {'detail': '카드를 찾을 수 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

    # 기존 좋아요 확인
    existing = UserEvent.objects.filter(
        user=request.user,
        card=card,
        event_type='LIKE'
    ).first()

    if existing:
        existing.delete()
        liked = False
    else:
        UserEvent.objects.create(
            user=request.user,
            card=card,
            event_type='LIKE',
            context={'source': 'toggle'}
        )
        liked = True

    like_count = UserEvent.objects.filter(card=card, event_type='LIKE').count()
    return Response({'liked': liked, 'like_count': like_count})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_liked_cards(request):
    """
    GET /cards/my/liked/ - 좋아요한 카드 목록
    """
    liked_events = UserEvent.objects.filter(
        user=request.user,
        event_type='LIKE'
    ).select_related('card').order_by('-created_at')

    cards = [event.card for event in liked_events if event.card]
    serializer = CardListSerializer(cards, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_recent_cards(request):
    """
    GET /cards/my/recent/ - 최근 본 카드 목록 (VIEW 이벤트 기반)
    """
    viewed_events = UserEvent.objects.filter(
        user=request.user,
        event_type='VIEW'
    ).select_related('card').order_by('-created_at')[:50]

    seen = set()
    cards = []
    for event in viewed_events:
        if event.card and event.card_id not in seen:
            seen.add(event.card_id)
            cards.append(event.card)
            if len(cards) >= 10:
                break

    serializer = CardListSerializer(cards, many=True, context={'request': request})
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_recommendation_history(request):
    """
    GET /cards/my/recommendations/ - 추천 이력 조회
    """
    logs = RecommendationLog.objects.filter(
        user=request.user
    ).order_by('-created_at')[:20]

    data = []
    for log in logs:
        cards = Card.objects.filter(id__in=log.result_card_ids)
        card_map = {c.id: c for c in cards}

        result_cards = []
        for cid, score in zip(log.result_card_ids, log.result_scores):
            card = card_map.get(cid)
            if card:
                result_cards.append({
                    'card': CardListSerializer(card, context={'request': request}).data,
                    'score': score
                })

        data.append({
            'id': log.id,
            'query_text': log.query_text,
            'filters': log.filters,
            'result_cards': result_cards[:3],
            'created_at': log.created_at
        })

    return Response(data)
