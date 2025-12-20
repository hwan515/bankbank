<script setup>
import { computed } from 'vue';
import { useRouter, RouterLink } from 'vue-router';
// 상태 관리를 위한 Pinia Store 가정 (User Store)
import { useUserStore } from '@/stores/user';
import { useAccountStore } from '@/stores/account';

const router = useRouter();
const accountStore = useAccountStore();

// 로그인 상태 체크 (보안: 토큰 유무 및 유효성 검증 로직 포함 필요)

const handleLogout = () => {
  accountStore.logout();
  router.push({ name: 'main' });
};

// 메뉴 구조화 (확장성 고려)
const menuItems = [
  { name: '예적금 비교', routeName: 'deposit-list' },
  { name: '현물 상품', routeName: 'commodities' },
  { name: '관심 종목', routeName: 'stocks' },
  { name: '은행 지도', routeName: 'bank-map' },
  { name: '카드 추천', routeName: 'card-recommendation' },
  { name: '커뮤니티', routeName: 'community' },
];
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light sticky-top shadow-sm">
    <div class="container-fluid">
      <RouterLink :to="{ name: 'main' }" class="navbar-brand fw-bold text-primary">
        Bankbook
      </RouterLink>

      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarContent">
        <span class="navbar-toggler-icon"></span>
      </button>

      <div class="collapse navbar-collapse" id="navbarContent">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">
          <li v-for="item in menuItems" :key="item.name" class="nav-item">
            <RouterLink :to="{ name: item.routeName }" class="nav-link">
              {{ item.name }}
            </RouterLink>
          </li>
        </ul>

        <div class="d-flex gap-2">
          <template v-if="!accountStore.isLogin">
            <RouterLink :to="{ name: 'login' }" class="btn btn-outline-primary btn-sm">로그인</RouterLink>
            <RouterLink :to="{ name: 'signup' }" class="btn btn-primary btn-sm">회원가입</RouterLink>
          </template>
          <template v-else>
            <RouterLink :to="{ name: 'profile' }" class="btn btn-outline-secondary btn-sm">마이페이지</RouterLink>
            <button @click="handleLogout" class="btn btn-secondary btn-sm">로그아웃</button>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<style scoped>
/* 금융 앱 특유의 깔끔하고 신뢰감을 주는 스타일링 */
.navbar-brand {
  font-family: 'Noto Sans KR', sans-serif;
  letter-spacing: -0.5px;
}
</style>