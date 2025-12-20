import { createRouter, createWebHistory } from 'vue-router'
import MainView from '../views/MainView.vue'

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
      component: { template: '<h1>Stocks</h1>' }
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
      component: { template: '<h1>Login</h1>' }
    },
    {
      path: '/signup',
      name: 'signup',
      component: { template: '<h1>Signup</h1>' }
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
    }
  ]
})

export default router