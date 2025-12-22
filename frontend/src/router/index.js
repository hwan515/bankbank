import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import LoginView from '@/views/accounts/LoginView.vue'
import RegisterView from '@/views/accounts/RegisterView.vue'
import StockMainView from '@/views/stock/stockMainView.vue'
import VideoDetailView from '@/views/stock/VideoDetailView.vue'
import ProductsListView from '../views/ProductsListView.vue'
import DepositDetailView from '../views/DepositDetailView.vue'
import SavingDetailView from '../views/SavingDetailView.vue'
import PlaceholderView from '../views/PlaceholderView.vue'
import CardView from '../views/CardView.vue'
import CardDetailView from '../views/CardDetailView.vue'
import RoadMap from '@/views/banks/RoadMap.vue'
import MyPageView from '@/views/accounts/MyPageView.vue'
import ChartsView from '@/views/charts/chartsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: MainView
    },
    {
      path: '/products',
      name: 'products',
      component: ProductsListView
    },
    {
      path: '/products/deposit/:id',
      name: 'deposit-detail',
      component: DepositDetailView
    },
    {
      path: '/products/saving/:id',
      name: 'saving-detail',
      component: SavingDetailView
    },
    {
      path: '/commodities',
      name: 'commodities',
      component: ChartsView
    },
    {
      path: '/stocks',
      name: 'stocks',
      component: StockMainView,
    },
    {
      path: '/bank-map',
      name: 'bank-map',
      component: RoadMap,
    },
    {
      path: '/community',
      name: 'community',
      component: PlaceholderView,
      props: { title: '커뮤니티' }
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
    {
      path: '/profile',
      name: 'profile',
      component: MyPageView
    },
    // 카드 관련 라우트
    {
      path: '/cards',
      name: 'cards',
      component: CardView
    },
    {
      path: '/card-recommendation',
      name: 'card-recommendation',
      component: { template: '<h1>card-recommendation</h1>' }
    },
    {
      path: '/videos/:id',
      name: 'VideoDetail',
      component: () => import ('@/views/stock/VideoDetailView.vue'),
      path: '/cards/:id',
      name: 'card-detail',
      component: CardDetailView
    }
  ]
})

export default router
