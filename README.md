# 통합 금융 서비스 bankbank

**"은행에 은행을 더하다"**

BankBank는 예금부터 카드 추천까지 다양한 금융 서비스를 한곳에서 경험할 수 있는 올인원 금융 플랫폼입니다.

## 👥 팀 소개 및 역할

### 팀장: 정지환

- 예적금 데이터 관리, 카드 데이터 크롤링 및 파이프라인 구축
- ChromaDB 기반 카드 추천 시스템
- OpenAI 챗봇 시스템 구현
- 커뮤니티 기능

### 팀원: 원대안

- 현물 데이터 시각화
- 근처 은행 검색 및 길 안내
- Youtube API 연동 영상 아카이빙
- WebSocket 채팅 시스템 구축

---

## ✨ 주요 기능

### 1. 금융 상품 비교 및 추천

- **예금/적금 비교**: 은행 상품을 기간, 적립 방식, 월 납입액 기준으로 필터링 및 비교 (금리, 우대 조건 확인).
- **맞춤형 카드 추천**: 사용자 소비 패턴 및 자연어 질의를 분석하여 최적의 카드 추천 (ChromaDB 벡터 검색).

### 2. AI 금융 비서

- **AI 챗봇 상담**: OpenAI 기반 챗봇이 자연어 질의를 이해하고 상품 추천 및 조회 수행.
- **개인화 서비스**: "내가 가입한 상품 알려줘"와 같은 개인화된 질문 처리.

### 3. 실시간 소통 및 정보

- **실시간 채팅**: WebSocket 기반 공개방(로비) 및 1:1 DM 지원.
- **커뮤니티**: 금융 정보 공유 게시판 (CRUD, 댓글, 좋아요).
- **현물 시세**: 금, 은 주요 현물 자산의 시세 차트 제공.

### 4. 편의 기능

- **근처 은행 검색**: 카카오맵 API 연동 위치 기반 은행 찾기 및 길 안내.
- **관심 영상 저장**: YouTube 금융 관련 영상 검색 및 아카이빙.

---

## 🗄️ ERD

![financedb](./images/financedb.png)

---

## 🖼️ wireframe

![financedb](./images/wireframe.png)

---

## ⚙️ 핵심 기술 및 로직

### 1. 하이브리드 카드 추천 시스템

사용자의 성향과 자연어 질의를 결합한 두 가지 추천 알고리즘을 제공합니다.

#### 추천 방식

1. **하이브리드 추천 (Hybrid)**: 자연어 질의(Semantic) + 사용자 선호도(Fit) + 인기도(Ranking)
   ![Hybrid_recommender](./images/Hybrid_recommender.jpg)
2. **프로필 기반 추천 (Profile-based)**: 사용자 선호 카테고리(Fit) + 인기도(Ranking)
   ![profile_based_recommender](./images/profile_based_recommender.jpg)

#### 점수 산정 로직

> **Hybrid Score** = (0.5 × Vector Similarity) + (0.5 × Category Fit) + Ranking Bonus

| 점수 요소          | 설명                                                |
| ------------------ | --------------------------------------------------- |
| **Semantic Score** | ChromaDB 벡터 검색 유사도 (자연어 질의 ↔ 카드 혜택) |
| **Fit Score**      | 사용자 선호 카테고리와 카드 혜택 매칭도             |
| **Ranking Bonus**  | 인기 순위 보너스: `max(0, (100 - ranking) / 1000)`  |

> **참고**: 연회비/전월실적 조건은 SQL 하드 필터로 사전 처리되어, 조건을 충족하지 않는 카드는 후보군에서 제외

#### 카테고리 분류 (15종)

| 코드    | 카테고리 | 코드    | 카테고리 |
| ------- | -------- | ------- | -------- |
| TRANS   | 교통     | COFFEE  | 카페     |
| COMM    | 통신     | FOOD    | 음식     |
| SHOP    | 쇼핑     | GAS     | 주유     |
| UTIL    | 공과금   | SUB     | 구독     |
| PAY     | 간편결제 | TRAVEL  | 여행     |
| MART    | 마트     | CULTURE | 문화     |
| MEDICAL | 의료     | EDU     | 교육     |
| ETC     | 기타     |         |          |

#### 임베딩 텍스트 구성

각 카드는 다음 정보를 조합하여 벡터화

- 카드명, 발급사, 카드종류
- 연회비, 전월실적 조건
- 혜택 요약 및 카테고리별 상세 혜택

#### 데이터 파이프라인 (Data Pipeline)

최신 카드 데이터를 유지하기 위해 4단계 자동화 파이프라인을 구축했습니다.

1. **Crawl**: `Card-Gorilla API`에서 데이터 수집 (SQLite 저장)
2. **Migrate**: SQLite 데이터를 서비스용 MySQL로 이관
3. **Refine**: GPT-4o-mini를 활용해 비정형 혜택 텍스트를 정형 JSON으로 변환
4. **Sync**: `text-embedding-3-large` 모델로 벡터화하여 ChromaDB 동기화

### 2. AI 챗봇 (Function Calling)

단순 대화를 넘어 실제 DB 데이터를 조회하여 답변하는 에이전트형 챗봇입니다.

- **모델**: GPT-4o-mini
- **Function Calling**: 사용자의 의도를 파악하여 적절한 내부 API(Tool)를 호출
  - `recommend_cards`: 벡터 검색 기반 카드 추천
  - `search_deposit/saving`: 예적금 상품 필터링 검색
  - `get_my_subscriptions`: 로그인 유저의 가입 상품 조회

### 3. 실시간 채팅 시스템 (WebSocket)

Django Channels와 Redis를 활용한 실시간 양방향 채팅 시스템입니다.

#### 주요 기능

| 기능                    | 설명                                              |
| ----------------------- | ------------------------------------------------- |
| **공개 채팅방 (Lobby)** | 모든 사용자가 참여 가능한 공용 채팅방             |
| **1:1 DM**              | 두 사용자 간의 비공개 대화 (`dm_key`로 중복 방지) |
| **실시간 브로드캐스트** | Redis Channel Layer를 통한 메시지 동기화          |
| **메시지 히스토리**     | DB 저장으로 채팅 기록 조회 가능                   |

#### 핵심 구현

- **Consumer (WebSocket Handler)**: `AsyncWebsocketConsumer` 기반 비동기 처리
- **인증**: Token 기반 WebSocket 미들웨어로 사용자 검증
- **Channel Group**: 채팅방별 그룹 관리 (`chat_{room_id}`)
- **메시지 저장**: `database_sync_to_async`로 비동기 DB 작업

```python
# 메시지 브로드캐스트 흐름
await self.channel_layer.group_send(
    f"chat_{room_id}",
    {"type": "chat_message", "sender": username, "message": content}
)
```

---

## 🏗 시스템 아키텍처 및 인프라

### Architecture Diagram

![Arichitecture_diagram](./images/Arichitecture_diagram.jpg)

### 기술 스택 (Tech Stack)

- **Backend**: Django DRF, Django Channels (Daphne)
- **Frontend**: Vue.js, Vite, Nginx
- **Database**: MySQL (Main), ChromaDB (Vector), Redis (Message Broker)
- **AI/ML**: OpenAI API (GPT-4o-mini, text-embedding-3-large)
- **Infra**: Docker, Docker Compose

### 환경 변수 설정 (.env)

```bash
# Django & Security
DJANGO_SECRET_KEY=...
DEBUG=False
ALLOWED_HOSTS=bank.cocohwan.site

# Databases
MYSQL_HOST=...
MYSQL_PASSWORD=...
REDIS_HOST=...

# External APIs
GMS_KEY=... (OpenAI Proxy Key)
FIN_API_KEY=... (Financial Supervisory Service)
YOUTUBE_API_KEY=...

```

---

## 🚀 배포 및 실행 (Deployment)

### Docker Compose 실행

전체 서비스는 Docker Compose를 통해 원클릭으로 배포됩니다.

```bash
# 1. 이미지 빌드
docker build -t hwan515/bankbank-be:latest ./backend
docker build -t hwan515/bankbank-fe:latest ./frontend \
  --build-arg VITE_API_BASE_URL=https://api.bank.cocohwan.site \
  --build-arg VITE_WS_BASE_URL=wss://api.bank.cocohwan.site

# 2. 컨테이너 실행
docker-compose up -d

```

### 데이터 파이프라인 실행 (초기 세팅)

서비스 구동 후 카드 데이터를 적재하려면 아래 명령어를 순차적으로 실행합니다.

```bash
# 1. 크롤링
cd analyze_card && python card_crawler.py

# 2. 데이터 이관
cd ../backend && python manage.py migrate_cards

# 3. 혜택 데이터 정제 (AI)
cd ../analyze_card && python benefit_refine_data.py

# 4. 벡터 DB 동기화
cd ../backend && python manage.py sync_chroma --all

```

---

## 🤖 생성형 AI 활용 내용

개발 전 과정에서 Claude Code를 활용하여 생산성과 코드 품질을 높였습니다.

| 활용 영역           | 상세 내용                                                    |
| ------------------- | ------------------------------------------------------------ |
| **추천 로직 설계**  | 하이브리드 추천 알고리즘 점수 산정 로직 검토 및 개선         |
| **파이프라인 구축** | 크롤링 → 정제 → 임베딩 → 동기화 4단계 데이터 파이프라인 설계 |
| **코드 리팩토링**   | 불필요한 패널티 로직 제거, 가중치 통일 등 코드 최적화        |
| **N+1 쿼리 개선**   | Django ORM `select_related`, `prefetch_related` 적용         |
| **UI/UX 통합**      | 컴포넌트별 CSS 스타일 통일 및 반응형 디자인 적용             |

---

## 🔧 트러블슈팅 (Troubleshooting)

### 1. 챗봇 API 401 인증 오류

**증상**: 챗봇에서 메시지 전송 시 401 Unauthorized 에러 발생

**원인**: `chatbot.js`에서 일반 axios를 사용하여 인증 토큰이 헤더에 포함되지 않음

**해결**:

```javascript
// Before
import axios from "axios";
axios.post("/api/chatbot/", { message });

// After
import api from "./api"; // 인터셉터에 토큰 자동 포함
api.post("/api/chatbot/", { message });
```

---

### 2. MySQL Migrations 에러

**증상**: db를 sqlite에서 mysql로 변경 후 migrate가 안되는 이유

**원인**:

- Django의 `TextField`는 MySQL에서 `LONGTEXT` 타입으로 생성
- MySQL은 데이터 크기가 정해지지 않은 `TEXT`나 `BLOB` 타입 컬럼에는 길이 제한 없이 `Unique Index`를 걸 수 없음

**해결**:

```django
//models.py

// Before
fin_prdt_cd = models.TextField()

// After
fin_prdt_cd = models.CharField(max_length=100, unique=True)
```

---

### 3. 상세페이지 뒤로가기 탭 오류

**증상**: 적금 상세페이지에서 "목록으로" 클릭 시 예금 탭으로 이동

**원인**: 뒤로가기 링크에 탭 상태를 전달하는 쿼리 파라미터가 누락됨

**해결**:

```vue
<!-- Before -->
<router-link to="/products">← 목록으로</router-link>

<!-- After -->
<router-link to="/products?tab=saving">← 목록으로</router-link>
```

---

### 4. 카드 추천 점수 계산 최적화

**증상**: 패널티 계산 함수가 항상 0을 반환하여 무의미한 연산 발생

**원인**: SQL 하드 필터에서 이미 조건 미충족 카드가 제외되어 패널티 로직이 불필요

**해결**:

- `_calc_penalty()`, `_calc_fee_penalty()` 메서드 삭제
- 가중치 단순화: `0.50 × Semantic + 0.50 × Fit + Ranking Bonus`
- `recommend()`와 `recommend_by_profile()` 간 가중치 통일

---

## 프로젝트 회고록

### 정지환

이번 1학기 동안 배운 내용과 그동안 쌓아 온 역량을 바탕으로 진행한 프로젝트였습니다. 특히 카드 데이터 정규화 과정에서 프롬프트 조건에 따라 데이터가 예상과 다르게 들어가거나 누락되는 문제가 반복적으로 발생하여 원인을 추적하고 처리 로직을 안정화하는 데 가장 많은 시간을 쏟았습니다. 그 과정에서 예외 케이스를 분리해 데이터 품질을 높이는 방법을 습득할 수 있었습니다. 또한 크롤링 과정에서 페이지를 분석하고 정제하는 방법 AI 수업에서 배운 내용을 참고해 추천 로직을 직접 설계하고 임베딩·벡터 검색 기반 파이프라인을 구성해 서비스에 적용했습니다. 결과적으로 이번 프로젝트는 설계, 구현, 검증까지 전체 개발 사이클을 경험하여 한 단계 성장할 수 있었습니다.
