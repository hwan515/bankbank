from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Card
from .serializers import CardListSerializer, CardRecommendRequestSerializer


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
