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
      <RouterLink :to="{ name: 'main' }" class="navbar-brand brand">
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

<script setup>
import { computed } from 'vue';
import { useRouter, RouterLink } from 'vue-router';
import { useUserStore } from '@/stores/user';

const router = useRouter();
const userStore = useUserStore();

const isLoggedIn = computed(() => userStore.isAuthenticated);

const handleLogout = () => {
  userStore.logout();
  router.push({ name: 'main' });
};

// 메뉴 항목
const menuItems = [
  { name: '예적금 비교', routeName: 'products' },
  { name: '카드', routeName: 'cards' },
  { name: '현물 상품', routeName: 'commodities' },
  { name: '관심 종목', routeName: 'stocks' },
  { name: '은행 지도', routeName: 'bank-map' },
  { name: '커뮤니티', routeName: 'community' },
];
</script>

<style scoped>
/* 유리 느낌 + 미니멀 */
.app-nav {
  background: rgba(255,255,255,0.86);
  border-bottom: 1px solid #efefef;
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
}

.brand {
  font-weight: 900;
  letter-spacing: -0.6px;
  color: #111;
  text-decoration: none;
}

.nav-links .nav-link {
  color: #444;
  font-weight: 600;
  font-size: 14px;
  padding: 10px 10px;
  border-radius: 10px;
}

.nav-links .nav-link:hover {
  background: #fafafa;
  color: #111;
}

.nav-links .nav-link.active {
  color: #111;
  position: relative;
}

.nav-links .nav-link.active::after {
  content: "";
  position: absolute;
  left: 10px;
  right: 10px;
  bottom: 6px;
  height: 2px;
  background: #111;
  border-radius: 999px;
}

/* 버튼 톤 통일 */
.btn {
  border-radius: 12px;
  font-weight: 700;
  padding: 8px 12px;
  border: 1px solid transparent;
}

.btn-ghost {
  background: #fff;
  border-color: #e8e8e8;
  color: #222;
}
.btn-ghost:hover { background: #fafafa; }

.btn-solid {
  background: #111;
  color: #fff;
}
.btn-solid:hover { background: #000; }

.btn-muted {
  background: #f2f2f2;
  border-color: #e8e8e8;
  color: #222;
}
.btn-muted:hover { background: #ededed; }
</style>
