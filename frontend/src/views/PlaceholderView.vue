<template>
  <div class="container py-5 text-center">
    <h1 class="text-muted">{{ title }}</h1>
    <p class="text-secondary">이 페이지는 준비 중입니다.</p>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    default: '페이지'
  }
})
</script>
