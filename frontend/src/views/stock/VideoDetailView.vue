<template>
  <div class="video-detail">
    <div class="container py-4">
      <header class="head">
        <div>
          <p class="eyebrow">관심 종목 영상</p>
          <h1 class="title serif-title">영상 상세</h1>
          <p class="sub">관심 영상의 내용을 바로 확인하세요.</p>
        </div>
      </header>

      <section class="card ui-card">
        <div class="meta">videoId: {{ route.params.id }}</div>
        <div class="ratio ratio-16x9 mt-2">
          <iframe
            :src="`https://www.youtube.com/embed/${route.params.id}`"
            title="YouTube player"
            allowfullscreen
          ></iframe>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'
const route = useRoute()
</script>


<style scoped>
.video-detail {
  min-height: 100%;
  background:
    radial-gradient(900px 300px at 10% 0%, rgba(27, 95, 122, 0.10), transparent 60%),
    linear-gradient(180deg, var(--bg-alt) 0%, var(--bg) 100%);
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}

.eyebrow {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--muted);
  margin: 0 0 4px;
}

.title {
  margin: 0;
  font-size: clamp(20px, 2vw, 26px);
  font-weight: 700;
  color: var(--ink);
}

.sub {
  margin: 6px 0 0;
  font-size: 13px;
  color: var(--muted);
}

.card {
  border-radius: var(--radius-md);
  padding: 16px;
}

.meta {
  font-size: 12px;
  color: var(--muted);
}
</style>
