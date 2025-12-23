<template>
  <div class="container py-4">
    <Profile/>

    <!-- 로그인 상태일 때만 카드 섹션 표시 -->
    <CardSection v-if="isLogin" />
    <SubscriptionSection v-if="isLogin" />
  </div>
</template>

<script setup>
import Profile from '@/components/accounts/Profile.vue'
import CardSection from '@/components/accounts/CardSection.vue'
import SubscriptionSection from '@/components/accounts/SubscriptionSection.vue'
import { useAccountStore } from '@/stores/account'
import { storeToRefs } from 'pinia'

const accountStore = useAccountStore()
const { isLogin } = storeToRefs(accountStore)
</script>

<style scoped>
</style>
