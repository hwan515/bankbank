import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'
import LoginView from '@/views/accounts/LoginView.vue'
import RegisterView from '@/views/accounts/RegisterView.vue'
import StockMainView from '@/views/stock/stockMainView.vue'
import VideoDetailView from '@/views/stock/VideoDetailView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'main',
      component: MainView
    },
    {
      path: '/deposit-list',
      name: 'deposit-list',
      component: { template: '<h1>Deposit List</h1>' }
    },
    {
      path: '/commodities',
      name: 'commodities',
      component: { template: '<h1>Commodities</h1>' }
    },
    {
      path: '/stocks',
      name: 'stocks',
      component: StockMainView
    },
    {
      path: '/bank-map',
      name: 'bank-map',
      component: { template: '<h1>Bank Map</h1>' }
    },
    {
      path: '/community',
      name: 'community',
      component: { template: '<h1>Community</h1>' }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/signup',
      name: 'signup',
      component: RegisterView
    },
    {
      path: '/profile',
      name: 'profile',
      component: { template: '<h1>Profile</h1>' }
    },
    {
      path: '/card-recommendation',
      name: 'card-recommendation',
      component: { template: '<h1>card-recommendation</h1>' }
    },
    {
      path: '/videos/:id',
      name: 'VideoDetail',
      component: () => import ('@/views/stock/VideoDetailView.vue')
    }
  ]
})

export default router