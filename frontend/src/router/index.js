// src/router/index.js
import { createRouter, createWebHistory } from 'vue-router'
import MainView from '@/views/MainView.vue'
import LoginView from '@/views/accounts/LoginView.vue'
import RegisterView from '@/views/accounts/RegisterView.vue'
import StockMainView from '@/views/stock/stockMainView.vue'
import VideoDetailView from '@/views/stock/VideoDetailView.vue'
import ProductsListView from '@/views/products/ProductsListView.vue'
import DepositDetailView from '@/views/products/DepositDetailView.vue'
import SavingDetailView from '@/views/products/SavingDetailView.vue'
import CardView from '@/views/cards/CardView.vue'
import CardDetailView from '@/views/cards/CardDetailView.vue'
import RoadMap from '@/views/banks/RoadMap.vue'
import CommunityListView from '@/views/community/CommunityListView.vue'
import CommunityDetailView from '@/views/community/CommunityDetailView.vue'
import PostFormView from '@/views/community/PostFormView.vue'
import MyPageView from '@/views/accounts/MyPageView.vue'
import ChartsView from '@/views/charts/ChartsView.vue'

// store (가드에서 사용)
import { useAccountStore } from '@/stores/account'

const routes = [
  // ✅ 공개 페이지
  {
    path: '/',
    name: 'main',
    component: MainView,
  },
  {
    path: '/login',
    name: 'login',
    component: LoginView,
  },
  {
    path: '/signup',
    name: 'signup',
    component: RegisterView,
  },

  // ✅ 로그인 필요 페이지
  {
    path: '/products',
    name: 'products',
    component: ProductsListView,
    meta: { requiresAuth: true },
  },
  {
    path: '/products/deposit/:id',
    name: 'deposit-detail',
    component: DepositDetailView,
    meta: { requiresAuth: true },
  },
  {
    path: '/products/saving/:id',
    name: 'saving-detail',
    component: SavingDetailView,
    meta: { requiresAuth: true },
  },
  {
    path: '/commodities',
    name: 'commodities',
    component: ChartsView,
    meta: { requiresAuth: true },
  },
  {
    path: '/stocks',
    name: 'stocks',
    component: StockMainView,
    meta: { requiresAuth: true },
  },
  {
    path: '/videos/:id',
    name: 'video-detail',
    component: VideoDetailView,
    meta: { requiresAuth: true },
  },
  {
    path: '/bank-map',
    name: 'bank-map',
    component: RoadMap,
    meta: { requiresAuth: true },
  },
  {
    path: '/community',
    name: 'community',
    component: CommunityListView,
    meta: { requiresAuth: true },
  },
  {
    path: '/community/new',
    name: 'community-new',
    component: PostFormView,
    meta: { requiresAuth: true },
  },
  {
    path: '/community/:id',
    name: 'community-detail',
    component: CommunityDetailView,
    meta: { requiresAuth: true },
  },
  {
    path: '/community/:id/edit',
    name: 'community-edit',
    component: PostFormView,
    meta: { requiresAuth: true },
  },
  {
    path: '/profile',
    name: 'profile',
    component: MyPageView,
    meta: { requiresAuth: true },
  },
  {
    path: '/cards',
    name: 'cards',
    component: CardView,
    meta: { requiresAuth: true },
  },
  {
    path: '/cards/:id',
    name: 'card-detail',
    component: CardDetailView,
    meta: { requiresAuth: true },
  },

  // (선택) 없는 경로 처리
  // { path: '/:pathMatch(.*)*', redirect: { name: 'main' } },
]
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
})

/**
 * ✅ 전역 네비게이션 가드
 * - requiresAuth 라우트인데 로그인 안했으면 로그인으로
 * - redirect 쿼리에 원래 목적지 저장
 */
router.beforeEach((to) => {
  const accountStore = useAccountStore()

  const requiresAuth = to.matched.some((r) => r.meta?.requiresAuth)

  if (requiresAuth && !accountStore.isLogin) {
    return {
      name: 'login',
      query: { redirect: to.fullPath },
    }
  }

  // 로그인 한 상태에서 로그인/회원가입 페이지 접근하면 메인으로 보내고 싶으면(선택)
  // if ((to.name === 'login' || to.name === 'signup') && accountStore.isLogin) {
  //   return { name: 'main' }
  // }
})

export default router
