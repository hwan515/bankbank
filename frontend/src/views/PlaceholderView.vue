<template>
  <div class="page">
    <div class="container py-5 text-center">
      <h1 class="title serif-title">{{ title }}</h1>
      <p class="sub">이 페이지는 준비 중입니다.</p>
    </div>
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

<style scoped>
.page {
  min-height: 100%;
  background:
    radial-gradient(900px 300px at 10% 0%, rgba(27, 95, 122, 0.10), transparent 60%),
    linear-gradient(180deg, var(--bg-alt) 0%, var(--bg) 100%);
}

.title {
  color: var(--ink);
  font-weight: 700;
}

.sub {
  color: var(--muted);
}
</style>
