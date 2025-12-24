<script setup>
import { useRouter, RouterLink, useRoute } from 'vue-router'
import { useAccountStore } from '@/stores/account'

const router = useRouter()
const route = useRoute()
const accountStore = useAccountStore()

const handleLogout = () => {
  accountStore.logout()
  router.push({ name: 'main' })
}

const menuItems = [
  { name: '예적금 비교', routeName: 'products' },
  { name: '카드', routeName: 'cards' },
  { name: '현물 상품', routeName: 'commodities' },
  { name: '관심 종목', routeName: 'stocks' },
  { name: '은행 지도', routeName: 'bank-map' },
  { name: '커뮤니티', routeName: 'community' },
]
</script>

<template>
  <nav class="navbar navbar-expand-lg sticky-top app-nav">
    <div class="container-fluid px-3 px-lg-4">
      <RouterLink :to="{ name: 'main' }" class="navbar-brand brand serif-title">
        BankBank
      </RouterLink>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarContent">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0 nav-links">
          <li v-for="item in menuItems" :key="item.name" class="nav-item">
            <RouterLink
              :to="{ name: item.routeName }"
              class="nav-link"
              :class="{ active: route.name === item.routeName }"
            >
              {{ item.name }}
            </RouterLink>
          </li>
        </ul>

        <div class="d-flex gap-2 align-items-center">
          <template v-if="!accountStore.isLogin">
            <RouterLink :to="{ name: 'login' }" class="btn btn-ghost btn-sm">로그인</RouterLink>
            <RouterLink :to="{ name: 'signup' }" class="btn btn-solid btn-sm">회원가입</RouterLink>
          </template>
          <template v-else>
            <RouterLink :to="{ name: 'profile' }" class="btn btn-ghost btn-sm">마이페이지</RouterLink>
            <button @click="handleLogout" class="btn btn-muted btn-sm">로그아웃</button>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>


<style scoped>
/* 유리 느낌 + 미니멀 */
.app-nav {
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.9), rgba(251, 249, 245, 0.85));
  border-bottom: 1px solid var(--border);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-shadow: 0 6px 16px rgba(16, 24, 40, 0.06);
}

.brand {
  font-weight: 700;
  letter-spacing: -0.4px;
  color: var(--ink);
  text-decoration: none;
}

.nav-links .nav-link {
  color: var(--ink-soft);
  font-weight: 600;
  font-size: 14px;
  padding: 10px 10px;
  border-radius: 999px;
}

.nav-links .nav-link:hover {
  background: var(--bg-alt);
  color: var(--ink);
}

.nav-links .nav-link.active {
  color: var(--ink);
  position: relative;
}

.nav-links .nav-link.active::after {
  content: "";
  position: absolute;
  left: 12px;
  right: 12px;
  bottom: 6px;
  height: 2px;
  background: var(--accent);
  border-radius: 999px;
}

/* 버튼 톤 통일 */
.btn {
  border-radius: 999px;
  font-weight: 600;
  padding: 8px 12px;
  border: 1px solid transparent;
}

.btn-ghost {
  background: var(--surface);
  border-color: var(--border);
  color: var(--ink-soft);
}
.btn-ghost:hover { background: var(--bg-alt); color: var(--ink); }

.btn-solid {
  background: var(--accent);
  color: #fff;
}
.btn-solid:hover { background: var(--accent-strong); }

.btn-muted {
  background: var(--bg-alt);
  border-color: var(--border);
  color: var(--ink-soft);
}
.btn-muted:hover { background: #f4efe6; color: var(--ink); }
</style>
