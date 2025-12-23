<script setup>
import ServiceCarousel from '@/components/main/ServiceCarousel.vue'

const services = [
  { title: '예·적금 비교', desc: '금리/우대 조건을 빠르게 비교', to: { name: 'products' } },
  { title: '카드 추천', desc: '소비 패턴 기반 추천/혜택 비교', to: { name: 'cards' } },
  { title: '은행 지도', desc: '내 주변 은행 찾고 경로 보기', to: { name: 'bank-map' } },
  { title: '커뮤니티', desc: '정보 공유/후기/질문 답변', to: { name: 'community' } },
]
</script>

<template>
  <div class="container py-4 main">
    <section class="mb-4 reveal-up">
      <ServiceCarousel />
    </section>

    <section class="mb-3">
      <div class="head">
        <h3 class="title serif-title">주요 금융 서비스</h3>
        <p class="sub">필요한 기능을 큐레이션해 빠르게 시작하세요.</p>
      </div>
    </section>

    <section class="grid mb-4">
      <RouterLink v-for="s in services" :key="s.title" :to="s.to" class="service-card ui-card reveal-up">
        <div class="card-title">{{ s.title }}</div>
        <div class="card-desc">{{ s.desc }}</div>
        <div class="card-arrow">→</div>
      </RouterLink>
    </section>
  </div>
</template>

<style scoped>
.main {
  max-width: 1120px;
  padding-bottom: 28px;
}

.head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.title {
  margin: 0;
  font-weight: 700;
  letter-spacing: -0.3px;
  color: var(--ink);
  font-size: clamp(18px, 1.8vw, 22px);
}

.sub {
  margin: 0;
  font-size: 13px;
  color: var(--muted);
}

.grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
}

.service-card {
  text-decoration: none;
  color: inherit;
  border-radius: var(--radius-md);
  padding: 18px;
  position: relative;
  transition: transform 0.2s ease, box-shadow 0.2s ease, border-color 0.2s ease;
}

.service-card:hover {
  transform: translateY(-3px);
  border-color: rgba(27, 95, 122, 0.35);
  box-shadow: var(--shadow-2);
}

.card-title {
  font-weight: 700;
  font-size: 15px;
  color: var(--ink);
  margin-bottom: 8px;
}

.card-desc {
  font-size: 13px;
  color: var(--ink-soft);
  line-height: 1.45;
  padding-right: 18px;
}

.card-arrow {
  position: absolute;
  right: 14px;
  bottom: 12px;
  color: var(--muted);
  font-weight: 700;
}

@media (max-width: 992px) {
  .grid { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}

@media (max-width: 576px) {
  .head { flex-direction: column; align-items: flex-start; }
  .grid { grid-template-columns: 1fr; }
}
</style>
