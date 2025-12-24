# Vue 3 Route Component Structure

이 문서는 Vue 3 프론트엔드에서 라우트(페이지) 기준으로 어떤 뷰/컴포넌트가 사용되는지 정리한 구조도입니다.

- 장고의 앱별로 뷰를 나눠서 관리
- 기본적은 뼈대는 네이밍 컨벤션은 AI활용후 코드 작성
- 이후, AI를 활용하여 리펙토링 및 코드 수정

## 공통 레이아웃 (모든 라우트)

- `src/App.vue`
  - `src/components/main/Navbar.vue`
  - `RouterView`
  - `src/components/chatbot/ChatbotWidget.vue`
  - `src/components/ui/ToastHost.vue`

## Routes

### `/` (name: `main`)

- `src/views/MainView.vue`
  - `src/components/main/ServiceCarousel.vue`

### `/login` (name: `login`)

- `src/views/accounts/LoginView.vue`

### `/signup` (name: `signup`)

- `src/views/accounts/RegisterView.vue`

### `/products` (name: `products`)

- `src/views/products/ProductsListView.vue`

### `/products/deposit/:id` (name: `deposit-detail`)

- `src/views/products/DepositDetailView.vue`
  - `src/composables/useProductDetail.js`

### `/products/saving/:id` (name: `saving-detail`)

- `src/views/products/SavingDetailView.vue`
  - `src/composables/useProductDetail.js`

### `/commodities` (name: `commodities`)

- `src/views/charts/ChartsView.vue`

### `/stocks` (name: `stocks`)

- `src/views/stock/stockMainView.vue`
  - `src/components/stock/VideoList.vue`
    - `src/components/stock/SearchButton.vue`
    - `src/components/stock/VideoListItem.vue`

### `/videos/:id` (name: `video-detail`)

- `src/views/stock/VideoDetailView.vue`

### `/bank-map` (name: `bank-map`)

- `src/views/banks/RoadMap.vue`
  - `src/components/bank/BankMap.vue`
    - `src/components/bank/SearchBar.vue`

### `/community` (name: `community`)

- `src/views/community/CommunityListView.vue`

### `/community/new` (name: `community-new`)

- `src/views/community/PostFormView.vue`

### `/community/:id` (name: `community-detail`)

- `src/views/community/CommunityDetailView.vue`

### `/community/:id/edit` (name: `community-edit`)

- `src/views/community/PostFormView.vue`

### `/profile` (name: `profile`)

- `src/views/accounts/MyPageView.vue`
  - `src/components/accounts/Profile.vue`
    - `src/components/accounts/EditModal.vue`
    - `src/components/accounts/InfoModal.vue`
  - `src/components/accounts/CardSection.vue`
    - `src/components/accounts/CardMiniItem.vue`
    - `src/components/accounts/PreferenceForm.vue`
  - `src/components/accounts/SubscriptionSection.vue`

### `/cards` (name: `cards`)

- `src/views/cards/CardView.vue`
  - `src/components/shared/LoadingSpinner.vue`
  - `src/components/cards/CardListItem.vue`
    - `src/components/shared/CardImage.vue`

### `/cards/:id` (name: `card-detail`)

- `src/views/cards/CardDetailView.vue`
  - `src/components/shared/LoadingSpinner.vue`
  - `src/components/shared/CardImage.vue`
